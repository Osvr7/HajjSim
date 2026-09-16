"""HTTP backend for the HajjSim dashboard.

This module serves the static web dashboard from the ``web`` folder and exposes
small JSON API endpoints that the frontend uses to create agents, update the
environment, advance the simulation, and read operational metrics.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Agent model helpers provide all simulation behavior; this file only exposes
# that behavior through a lightweight local HTTP API.
from hajj_agents import (
    AgentFactory,
    build_agent_from_record,
    build_manual_agent,
    get_simulation_day_payload,
    get_simulation_tick_payload,
    get_ritual_schedule_payload,
    NODE_CAPACITY_BASELINES,
    DEFAULT_NODE_CAPACITY,
    SIGNIFICANT_RISK_LEVELS,
)

# The LLM decision layer, its structured log, and the after-action report are
# each self-contained modules so the model can be swapped without touching the
# simulation or this HTTP layer.
from llm_decision import LLMDecisionEngine, llm_decide_action, load_env_file
from simulation_log import DecisionRecord, SimulationLog, TickRecord
from analysis_report import build_simulation_report, render_markdown, write_report
from hajj_units import (
    ConvoyDispatchCoordinator,
    HamlahRegistry,
    
    HotelRegistry,
    OperationalUnit,
    UnitFactory,
    normalize_nationality,
)


# Project paths used by both the static file server and the API layer.
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web"
DATA_FILE = BASE_DIR / "pilgrims.json"
HAMLAH_DATA_FILE = BASE_DIR / "hamlahs.json"
HOTEL_DATA_FILE = BASE_DIR / "hotels.json"
ENV_FILE = BASE_DIR / ".env"

# Load .env before anything reads LLM_* settings. Variables already exported in
# the real environment win, so this only fills in what the shell did not set.
_LOADED_ENV_VARS = load_env_file(ENV_FILE)


@dataclass
class EnvironmentState:
    """Mutable simulation settings controlled by the dashboard.

    The environment is shared by every agent during a simulation step. It stores
    crowd density, heat, hazard type, group location, and the ritual tick.
    """

    density: float = 5.0
    temperature: float = 37.0
    hazard: str = "none"
    group_location: str = "Jeddah_Airport"
    alternate_node: str = "Shade_Corridor"
    panic_node: str = "Emergency_Point"
    tick: int = -1

    def _current_tick_state(self) -> dict:
        """Return the ritual/day metadata for the current tick."""
        return get_simulation_tick_payload(self.tick)

    def apply_updates(self, payload: dict) -> None:
        """Merge user-provided environment values while keeping them bounded."""
        # Numeric controls are clamped so browser/API input cannot push the
        # simulation outside the range expected by the agent decision rules.
        if "density" in payload:
            self.density = max(0.0, min(10.0, float(payload["density"])))
        if "temperature" in payload:
            self.temperature = max(20.0, min(50.0, float(payload["temperature"])))
        # Text controls choose the scenario nodes/hazards used during the next
        # simulation step, falling back to current defaults when blank.
        if "hazard" in payload:
            self.hazard = str(payload["hazard"] or "none")
        if "group_location" in payload:
            self.group_location = str(payload["group_location"] or self.group_location)
        if "alternate_node" in payload:
            self.alternate_node = str(payload["alternate_node"] or self.alternate_node)
        if "panic_node" in payload:
            self.panic_node = str(payload["panic_node"] or self.panic_node)

    def reset(self) -> None:
        """Restore environment controls to the initial dashboard state."""
        self.density = 5.0
        self.temperature = 37.0
        self.hazard = "none"
        self.group_location = "Jeddah_Airport"
        self.alternate_node = "Shade_Corridor"
        self.panic_node = "Emergency_Point"
        self.tick = -1

    def to_payload(self) -> dict:
        """Build the internal payload passed into every agent's decision loop."""
        tick_state = self._current_tick_state()
        # The agent layer expects internal field names and a real None when no
        # hazard is active.
        return {
            "density": self.density,
            "temperature": self.temperature,
            "hazard": None if self.hazard == "none" else self.hazard,
            "group_location": self.group_location,
            "alternate_node": self.alternate_node,
            "panic_node": self.panic_node,
            "tick": self.tick,
            "simulation_ritual_index": tick_state["simulation_ritual_index"],
            "simulation_day_index": tick_state["simulation_day_index"],
            "simulation_day_label": tick_state["simulation_day_label"],
            "current_ritual": tick_state["current_ritual"],
            "next_ritual": tick_state["next_ritual"],
            "next_ritual_day_label": tick_state["next_ritual_day_label"],
            "scheduled_rituals": list(tick_state["day_plan_rituals"]),
            "ritual_window_open": tick_state["ritual_window_open"],
            "simulated_minutes": tick_state["simulated_minutes"],
            "simulated_time_label": tick_state["simulated_time_label"],
        }

    def to_dict(self) -> dict:
        """Build the JSON-safe environment object returned to the frontend."""
        tick_state = self._current_tick_state()
        # The dashboard receives rounded values plus ritual metadata for labels,
        # timelines, and environment controls.
        return {
            "density": round(self.density, 2),
            "temperature": round(self.temperature, 2),
            "hazard": self.hazard,
            "group_location": self.group_location,
            "alternate_node": self.alternate_node,
            "panic_node": self.panic_node,
            "tick": max(self.tick + 1, 0),
            "simulation_ritual_index": tick_state["simulation_ritual_index"],
            "simulation_day_index": tick_state["simulation_day_index"],
            "simulation_day_label": tick_state["simulation_day_label"],
            "current_ritual": tick_state["current_ritual"],
            "next_ritual": tick_state["next_ritual"],
            "next_ritual_day_label": tick_state["next_ritual_day_label"],
            "day_plan_rituals": list(tick_state["day_plan_rituals"]),
            "ritual_day_label": tick_state["simulation_day_label"],
            "day_plan_label": " | ".join(tick_state["day_plan_rituals"]),
            "ritual_schedule": get_ritual_schedule_payload(),
            "simulation_days": get_simulation_day_payload(),
            "ritual_window_open": tick_state["ritual_window_open"],
            "simulated_minutes": tick_state["simulated_minutes"],
            "simulated_time_label": tick_state["simulated_time_label"],
        }


class AgentRepository:
    """In-memory collection of pilgrim agents.

    The repository loads the seed agents from ``pilgrims.json`` and then keeps
    generated/manual agents in memory for the current server session.
    """

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.factory = AgentFactory(seed=42)
        self.agents = {}
        self._next_index = 1
        self.load()

    def load(self) -> None:
        """Read seed pilgrim records from disk and rebuild agent objects."""
        # If the seed data is missing, keep the server usable with an empty
        # in-memory roster.
        if not self.data_file.exists():
            self.agents = {}
            self._next_index = 1
            return

        with self.data_file.open("r", encoding="utf-8") as file:
            records = json.load(file)

        self.agents = {}
        max_index = 0
        for record in records:
            # Each saved JSON record is converted back into the full four-layer
            # PilgrimAgent object used by the simulation.
            agent = build_agent_from_record(record, llm_override=llm_pilgrim_override)
            self.agents[agent.profile.pilgrim_id] = agent
            digits = "".join(char for char in agent.profile.pilgrim_id if char.isdigit())
            if digits:
                max_index = max(max_index, int(digits))
        self._next_index = max_index + 1 if max_index else 1

    def list_agents(self) -> list[dict]:
        """Return frontend-ready snapshots for all active agents."""
        return [agent.get_snapshot() for agent in self.agents.values()]

    def create_manual_agent(self, payload: dict, hamlah_registry: HamlahRegistry) -> dict:
        """Create one agent from the manual dashboard form.

        Every pilgrim must belong to a Hamlah whose nationality matches its
        own -- raises ValueError (caught by the HTTP handler as a 400) if
        hamlah_id is missing, unknown, or nationality-mismatched, instead of
        letting StaticProfile's own validation surface as an opaque 500.
        """
        pilgrim_id = payload.get("pilgrim_id") or f"P_{self._next_index:04d}"
        chronic_conditions = self._parse_conditions(payload.get("chronic_conditions", []))
        nationality = payload["nationality"]
        hamlah_id = payload.get("hamlah_id") or None

        if not hamlah_id:
            raise ValueError("hamlah_id is required -- every pilgrim must belong to a Hamlah")
        hamlah = hamlah_registry.hamlahs.get(hamlah_id)
        if hamlah is None:
            raise ValueError(f"Unknown hamlah_id {hamlah_id!r}")
        if normalize_nationality(hamlah.nationality) != normalize_nationality(nationality):
            raise ValueError(
                f"Nationality mismatch: pilgrim is {nationality!r} but Hamlah "
                f"{hamlah_id!r} is {hamlah.nationality!r}"
            )

        agent = build_manual_agent(
            pilgrim_id=pilgrim_id,
            age=int(payload["age"]),
            nationality=nationality,
            group_id=payload["group_id"],
            mobility=float(payload["mobility"]),
            health_status=payload["health_status"],
            initial_node=payload["initial_node"],
            target_node=payload["target_node"],
            language=payload.get("language", "Arabic"),
            chronic_conditions=chronic_conditions,
            risk_tolerance=float(payload.get("risk_tolerance", 0.5)),
            performs_sacrifice=self._parse_bool(payload.get("performs_sacrifice", True)),
            hamlah_id=hamlah_id,
            llm_override=llm_pilgrim_override,
        )
        self.agents[agent.profile.pilgrim_id] = agent
        self._advance_index(agent.profile.pilgrim_id)
        return agent.get_snapshot()

    def generate_random_agents(self, count: int, nationality_to_hamlah: dict) -> list[dict]:
        """Generate a synthetic population using demographic distributions.

        nationality_to_hamlah (one Hamlah per possible nationality) ensures
        every generated agent's Hamlah always matches its own nationality.
        """
        generated = self.factory.generate_agents(
            count=count,
            start_index=self._next_index,
            nationality_to_hamlah=nationality_to_hamlah,
            llm_override=llm_pilgrim_override,
        )
        self.agents.update(generated)
        self._next_index += count
        return [agent.get_snapshot() for agent in generated.values()]

    def step_all(
        self,
        environment_data: dict,
        hamlah_dispatch_offsets: dict | None = None,
        post_step_hook=None,
    ) -> list[dict]:
        """Advance every agent once and return the action each agent selected.

        ``post_step_hook(agent, action, environment)`` runs immediately after an
        agent's action has executed, which is where the LLM decision log records
        what the decision actually did to the world.
        """
        # Build group-location context first so every agent can decide whether
        # it is still near the majority of its group.
        group_locations = {}
        # Live occupancy per node: the LLM observation needs real congestion
        # numbers, not just the global density slider.
        node_counts: dict[str, int] = {}
        for agent in self.agents.values():
            group_locations.setdefault(agent.profile.group_id, []).append(agent.state.current_node)
            node_counts[agent.state.current_node] = node_counts.get(agent.state.current_node, 0) + 1

        # Add shared social/campaign context to the environment without
        # mutating the caller's original payload.
        step_environment = dict(environment_data)
        step_environment["group_locations"] = group_locations
        step_environment["node_counts"] = node_counts
        step_environment["hamlah_dispatch_offsets"] = hamlah_dispatch_offsets or {}

        # Run the full perceive-decide-act cycle for the active roster.
        actions = []
        for agent in self.agents.values():
            action = agent.step(step_environment)
            actions.append({"pilgrim_id": agent.profile.pilgrim_id, "action": action})
            if post_step_hook is not None:
                post_step_hook(agent, action, step_environment)
        return actions

    def reset_ritual_days(self) -> None:
        """Restart the ritual schedule while keeping the active agent roster."""
        for agent in self.agents.values():
            agent.reset_ritual_cycle()

    def reset_all(self) -> None:
        """Reload the original seed roster and remove generated session agents."""
        self.load()

    def _advance_index(self, pilgrim_id: str) -> None:
        """Keep generated IDs ahead of any manually supplied numeric ID."""
        digits = "".join(char for char in pilgrim_id if char.isdigit())
        if digits:
            self._next_index = max(self._next_index, int(digits) + 1)
        else:
            self._next_index += 1

    @staticmethod
    def _parse_conditions(value) -> list[str]:
        """Normalize chronic condition form input into a clean list."""
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    @staticmethod
    def _parse_bool(value) -> bool:
        """Accept checkbox-style values from both JSON and HTML forms."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)


class UnitRepository:
    """In-memory collection of support units (buses, marshals, police, ambulances)."""

    def __init__(self):
        self.factory = UnitFactory()
        self.units: dict[str, OperationalUnit] = {}
        self.spawn_default_fleet()

    def spawn_default_fleet(self) -> None:
        """(Re)populate the fixed default fleet used by the dashboard."""
        self.units = self.factory.spawn_default_fleet()

    def list_units(self) -> list[dict]:
        """Return frontend-ready snapshots for every support unit."""
        return [unit.to_payload() for unit in self.units.values()]

    def step_all(self, environment_data: dict, pilgrim_snapshots: list[dict]) -> list[dict]:
        """Advance every unit once and return the action each one selected."""
        actions = []
        for unit in self.units.values():
            action = unit.step(environment_data, pilgrim_snapshots)
            actions.append({"unit_id": unit.unit_id, "action": action})
        return actions

    def deploy_unit(self, unit_type: str, node_id: str) -> dict:
        """Manually click-to-place one police/marshal/ambulance unit."""
        if unit_type not in {"police", "marshal", "ambulance"}:
            raise ValueError(f"Cannot deploy unit_type {unit_type!r} -- buses are a fixed shared fleet")
        unit_id = f"{unit_type.upper()[:3]}_EXT_{sum(1 for u in self.units if u.startswith(f'{unit_type.upper()[:3]}_EXT_')) + 1:02d}"
        unit = self.factory.build_manual_unit(unit_type, unit_id, node_id)
        self.units[unit_id] = unit
        return unit.to_payload()


def derive_operational_status(agent: dict) -> str:
    """Classify a pilgrim into the status color shown on the dashboard."""
    state = agent.get("state", {})
    stress = float(state.get("stress", 0))
    fatigue = float(state.get("fatigue", 0))
    hydration = float(state.get("hydration", 100))

    # Panic overrides all other categories; otherwise vitals are bucketed into
    # high-risk, support-needed, or stable dashboard states.
    if state.get("is_panicking"):
        return "panicking"
    if stress >= 88 or fatigue >= 86 or hydration <= 28:
        return "high_risk"
    if stress >= 62 or fatigue >= 58 or hydration <= 62:
        return "needs_support"
    return "stable"


# ============================================================
# LLM decision layer wiring
# ------------------------------------------------------------
# The pilgrim agents already exposed a BehaviorEngine.llm_override hook; this
# section finally supplies a real callable for it. The rule-based ladder still
# runs first every tick and its result is handed to the model as the safe
# fallback, so a failed call, a timeout or a hallucinated action degrades to
# exactly the behavior the simulation had before.
# ============================================================

LLM_ENGINE = LLMDecisionEngine()
SIMULATION_LOG = SimulationLog()
REPORTS_DIR = BASE_DIR / "reports"
LAST_REPORT_PATHS: dict = {}

# Which pilgrims are model-driven this run (see LLM_MAX_AGENTS in the README).
LLM_AGENT_IDS: set = set()


def refresh_llm_agent_selection(agent_ids) -> set:
    """Pick the deterministic subset of pilgrims the LLM drives.

    A full run is 240 ticks; driving every pilgrim with a live model call would
    mean six-figure API calls. LLM_MAX_AGENTS caps it (0 = the whole roster),
    and the selection is the lowest pilgrim ids so a demo always shows the same
    agents and a re-run is comparable.
    """
    global LLM_AGENT_IDS
    max_agents = LLM_ENGINE.settings.max_agents
    ordered = sorted(agent_ids)
    LLM_AGENT_IDS = set(ordered) if max_agents <= 0 else set(ordered[:max_agents])
    return LLM_AGENT_IDS


def is_llm_driven(pilgrim_id: str) -> bool:
    """True when this pilgrim's action should come from the model this tick."""
    if not LLM_ENGINE.is_active:
        return False
    if LLM_ENGINE.settings.max_agents <= 0:
        return True
    return pilgrim_id in LLM_AGENT_IDS


def _risk_environment_snapshot(agent, environment_data: dict, observation: dict) -> dict:
    """Compact environment picture stored alongside a risk event."""
    location = observation.get("location", {})
    return {
        "crowd_density": observation.get("conditions", {}).get("crowd_density_0_to_10"),
        "temperature_c": observation.get("conditions", {}).get("temperature_c"),
        "hazard": observation.get("conditions", {}).get("hazard"),
        "occupancy": location.get("occupancy"),
        "capacity": location.get("capacity"),
        "congestion": location.get("congestion"),
        "zone": location.get("zone"),
        "current_ritual": environment_data.get("current_ritual"),
        "target_node": agent.state.target_node,
        "travel_state": agent.state.travel_state,
        "vitals": observation.get("vitals", {}),
    }


def llm_pilgrim_override(agent, environment_data: dict, proposed_action: str):
    """``BehaviorEngine.llm_override`` implementation: the LLM picks the action.

    Returns the chosen action string, or ``None`` to leave the rule-based
    decision in place (when the pilgrim is not model-driven, or when the convoy
    coordinator owns it this tick and there is no real choice to make).
    """
    pilgrim_id = agent.profile.pilgrim_id
    if not is_llm_driven(pilgrim_id):
        return None

    # Build the two halves of the contract: what the agent can see, and what
    # the engine is actually able to execute for it right now.
    available_actions = agent.available_actions(environment_data)
    if len(available_actions) == 1 and available_actions[0].get("kind") == "locked":
        # Boarded on a bus or queued for one -- not a decision, don't spend a call.
        return None

    state = agent.state
    observation = agent.build_observation(environment_data)
    simulated_time = str(environment_data.get("simulated_time_label") or "")

    # Risk events are tracked before the decision, so the event records the
    # situation the model was reacting to rather than its aftermath.
    SIMULATION_LOG.observe_risk(
        pilgrim_id=pilgrim_id,
        tick=state.simulation_tick,
        simulated_time=simulated_time,
        location=state.current_node,
        risk={
            "level": state.risk_level,
            "score": state.risk_score,
            "factors": list(state.risk_factors),
            "hazard": observation.get("conditions", {}).get("hazard"),
        },
        environment=_risk_environment_snapshot(agent, environment_data, observation),
        significant_levels=frozenset(SIGNIFICANT_RISK_LEVELS),
    )

    decision = llm_decide_action(
        environment_state=observation,
        available_actions=available_actions,
        fallback_action=proposed_action,
        engine=LLM_ENGINE,
    )

    action_kind = next(
        (entry.get("kind", "") for entry in available_actions if entry.get("action") == decision.action),
        "",
    )

    # Provenance lands on the agent so the dashboard sidebar can show who chose.
    state.last_decision_source = decision.source
    state.last_decision_reason = decision.reason
    state.last_fallback_action = decision.fallback_action or proposed_action

    SIMULATION_LOG.open_decision(DecisionRecord(
        tick=state.simulation_tick,
        simulated_time=simulated_time,
        pilgrim_id=pilgrim_id,
        location=state.current_node,
        zone=observation.get("location", {}).get("zone", ""),
        target_node=state.target_node,
        risk_level=state.risk_level,
        risk_score=state.risk_score,
        risk_factors=list(state.risk_factors),
        hazard=observation.get("conditions", {}).get("hazard"),
        crowd_density=observation.get("conditions", {}).get("crowd_density_0_to_10", 0.0),
        temperature_c=observation.get("conditions", {}).get("temperature_c", 0.0),
        congestion_ratio=observation.get("location", {}).get("congestion_ratio", 0.0),
        available_actions=[entry["action"] for entry in available_actions],
        action=decision.action,
        action_kind=action_kind,
        distance_hops=observation.get("ritual", {}).get("distance_hops", 0),
        reason=decision.reason,
        source=decision.source,
        fallback_action=decision.fallback_action,
        error=decision.error,
        latency_ms=decision.latency_ms,
        provider=decision.provider,
        model=decision.model,
        _stress_before=state.stress,
        _fatigue_before=state.fatigue,
        _hydration_before=state.hydration,
    ))
    return decision.action


def finalize_agent_decision(agent, action: str, environment_data: dict) -> None:
    """Close this pilgrim's pending decision record with the post-action result.

    Called by ``AgentRepository.step_all`` immediately after the action has
    executed, so the log captures what the decision actually did to the world:
    where the pilgrim ended up and how its risk and vitals moved.
    """
    risk_after = agent.assess_risk(environment_data)
    SIMULATION_LOG.close_decision(
        pilgrim_id=agent.profile.pilgrim_id,
        resulting_node=agent.state.current_node,
        risk_level_after=risk_after["level"],
        risk_score_after=risk_after["score"],
        stress_after=agent.state.stress,
        fatigue_after=agent.state.fatigue,
        hydration_after=agent.state.hydration,
    )


# Global simulation session state used by the HTTP handler.
REPOSITORY = AgentRepository(DATA_FILE)
HAMLAH_REGISTRY = HamlahRegistry(HAMLAH_DATA_FILE)
HOTEL_REGISTRY = HotelRegistry(HOTEL_DATA_FILE)
UNIT_REPOSITORY = UnitRepository()
CONVOY_COORDINATOR = ConvoyDispatchCoordinator()
ENVIRONMENT = EnvironmentState()
SUMMARY_HISTORY: list[dict] = []
DEPLOYMENT_LOG: list[dict] = []


def sync_hamlah_membership() -> None:
    """Recompute every Hamlah's live member list from the current agent roster."""
    HAMLAH_REGISTRY.rebuild_membership(
        (agent.profile.pilgrim_id, agent.profile.hamlah_id) for agent in REPOSITORY.agents.values()
    )


def sync_hotel_occupancy() -> None:
    """Recompute every hotel's live occupant list from the current agent roster."""
    HOTEL_REGISTRY.rebuild_occupancy(
        (agent.profile.pilgrim_id, agent.state.checked_in_hotel_id) for agent in REPOSITORY.agents.values()
    )


def build_hamlah_hotel_map() -> dict:
    """Join the Hamlah and Hotel registries into hamlah_id -> {hotel_id, hotel_node}."""
    hamlah_hotel_map = {}
    for hamlah in HAMLAH_REGISTRY.hamlahs.values():
        hotel = HOTEL_REGISTRY.hotels.get(hamlah.base_camp_hotel_id)
        if hotel:
            hamlah_hotel_map[hamlah.hamlah_id] = {"hotel_id": hotel.hotel_id, "hotel_node": hotel.node_id}
    return hamlah_hotel_map


sync_hamlah_membership()
sync_hotel_occupancy()
# Decide up front which pilgrims the model drives, so /api/llm/status is
# informative before the first simulation step is taken.
refresh_llm_agent_selection(REPOSITORY.agents.keys())


def build_summary_snapshot() -> dict:
    """Aggregate all agents into the top-level operational dashboard metrics."""
    # Start with counters that will become the hero summary and chart series.
    agents = REPOSITORY.list_agents()
    total = len(agents)
    stable = 0
    needs_support = 0
    high_risk = 0
    panicking = 0
    location_counts = {}

    # Count status buckets and current locations in one pass over the roster.
    for agent in agents:
        state = agent["state"]
        status = derive_operational_status(agent)
        location = state.get("current_node")
        if location:
            location_counts[location] = location_counts.get(location, 0) + 1

        if status == "panicking":
            panicking += 1
        elif status == "high_risk":
            high_risk += 1
        elif status == "needs_support":
            needs_support += 1
        else:
            stable += 1

    # Average vital signs and a weighted severity score summarize operational
    # pressure for the dashboard graph.
    avg_stress = round(sum(agent["state"]["stress"] for agent in agents) / total, 1) if total else 0.0
    avg_fatigue = round(sum(agent["state"]["fatigue"] for agent in agents) / total, 1) if total else 0.0
    avg_hydration = round(sum(agent["state"]["hydration"] for agent in agents) / total, 1) if total else 0.0
    severity_index = round(
        ((panicking * 1.0) + (high_risk * 0.7) + (needs_support * 0.4)) / total * 100,
        1,
    ) if total else 0.0

    leading_current_location = None
    if location_counts:
        # The leading location highlights where the biggest cluster currently is.
        leading_current_location = max(location_counts.items(), key=lambda item: item[1])[0]

    tick_state = ENVIRONMENT.to_dict()
    return {
        "total_agents": total,
        "stable_agents": stable,
        "panicking_agents": panicking,
        "needs_support_agents": needs_support,
        "high_risk_agents": high_risk,
        "avg_stress": avg_stress,
        "avg_fatigue": avg_fatigue,
        "avg_hydration": avg_hydration,
        "severity_index": severity_index,
        "simulation_tick": tick_state["tick"],
        "simulation_day_label": tick_state["simulation_day_label"],
        "current_ritual": tick_state["current_ritual"],
        "next_ritual": tick_state["next_ritual"],
        "leading_current_location": leading_current_location,
        "location_counts": location_counts,
    }


def update_summary_history() -> dict:
    """Store one summary point per ritual tick for the line chart."""
    summary = build_summary_snapshot()
    entry = {**summary}
    # Replace the current tick's entry when controls change without advancing
    # time; append only when a new ritual tick is reached.
    if SUMMARY_HISTORY and SUMMARY_HISTORY[-1]["simulation_tick"] == entry["simulation_tick"]:
        SUMMARY_HISTORY[-1] = entry
    else:
        SUMMARY_HISTORY.append(entry)
    return summary


def _average_pressure_ratio(entries: list[dict], node_id: str) -> float:
    """Average a node's count/capacity ratio across a slice of history entries."""
    capacity = NODE_CAPACITY_BASELINES.get(node_id, DEFAULT_NODE_CAPACITY)
    if not entries or not capacity:
        return 0.0
    ratios = [entry.get("location_counts", {}).get(node_id, 0) / capacity for entry in entries]
    return sum(ratios) / len(ratios)


def evaluate_deployment_impact(deployment_log: list[dict], history: list[dict], window: int = 3) -> list[dict]:
    """Compare pressure at a manually-deployed unit's node before vs. after deployment."""
    results = []
    for event in deployment_log:
        deploy_tick = event["tick"]
        node_id = event["node_id"]
        before = [h for h in history if deploy_tick - window <= h.get("simulation_tick", -1) < deploy_tick]
        after = [h for h in history if deploy_tick <= h.get("simulation_tick", -1) < deploy_tick + window]
        ratio_before = _average_pressure_ratio(before, node_id)
        ratio_after = _average_pressure_ratio(after, node_id)
        if ratio_after < ratio_before * 0.9:
            verdict = "reduced pressure"
        elif abs(ratio_after - ratio_before) < 0.05:
            verdict = "no measurable effect"
        else:
            verdict = "pressure kept rising"
        results.append({
            **event,
            "ratio_before": round(ratio_before, 2),
            "ratio_after": round(ratio_after, 2),
            "verdict": verdict,
        })
    return results


def _build_narrative_prompt(peak_bottlenecks: list[dict], resilient_windows: list[dict], deployment_impact: list[dict]) -> str:
    """Render the computed metrics into a plain-text prompt for the LLM narrative."""
    lines = [
        "Write a short (3-4 paragraph) after-action analytics narrative for a Hajj crowd-simulation "
        "operational report, based only on the following computed metrics. Be specific and factual; "
        "do not invent numbers or locations not listed below.",
        "",
        "Peak bottlenecks (node, peak pressure ratio vs. capacity, ticks overloaded):",
    ]
    for item in peak_bottlenecks:
        lines.append(f"- {item['node']}: {item['peak_ratio']}x capacity, {item['overload_ticks']} overloaded ticks")
    lines.append("")
    lines.append("Resilient (low-pressure) windows observed:")
    for item in resilient_windows:
        when_label = item["day_label"] or f"tick {item['tick']}"
        lines.append(f"- {when_label}: severity index {item['severity_index']}%")
    if deployment_impact:
        lines.append("")
        lines.append("Manually-deployed emergency units and their measured before/after effect:")
        for item in deployment_impact:
            lines.append(
                f"- {item['unit_type']} at {item['node_id']}: pressure ratio {item['ratio_before']} -> "
                f"{item['ratio_after']} ({item['verdict']})"
            )
    return "\n".join(lines)


def generate_narrative_via_llm(peak_bottlenecks: list[dict], resilient_windows: list[dict], deployment_impact: list[dict]) -> str | None:
    """Best-effort narrative via Google's Gemini free tier; None if not configured or it fails.

    Deliberately opt-in and dependency-free by default: if GEMINI_API_KEY
    isn't set, this returns immediately without even importing the package,
    so the app has zero external dependency until the user chooses to
    "fill it in later." Any failure (missing package, bad key, network,
    rate limit) falls back the same way -- the caller uses a template
    summary instead, so the report never breaks.
    """
    import os

    if not os.environ.get("GEMINI_API_KEY"):
        return None
    try:
        import google.generativeai as genai
    except ImportError:
        return None
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")  # free-tier model; verify the current name before relying on this
        prompt = _build_narrative_prompt(peak_bottlenecks, resilient_windows, deployment_impact)
        response = model.generate_content(prompt)
        return response.text or None
    except Exception as error:  # noqa: BLE001 -- any failure should fall back, not crash the report
        print(f"LLM narrative generation failed, falling back to template: {error}")
        return None


def _template_narrative(peak_bottlenecks: list[dict], resilient_windows: list[dict], deployment_impact: list[dict]) -> str:
    """Always-available fallback narrative when the optional LLM path isn't used."""
    if peak_bottlenecks:
        names = ", ".join(item["node"].replace("_", " ") for item in peak_bottlenecks[:2])
        overview = f"This run faced sustained crowd pressure at {names}."
    else:
        overview = "This run stayed within safe crowd-pressure thresholds throughout."

    parts = [overview]
    if resilient_windows:
        parts.append(
            f"{len(resilient_windows)} tick(s) showed particularly smooth, low-severity operation, "
            "indicating the crowd-management approach held up well during those windows."
        )
    if deployment_impact:
        reduced = sum(1 for item in deployment_impact if item["verdict"] == "reduced pressure")
        parts.append(
            f"Of {len(deployment_impact)} manually-deployed emergency unit(s) this run, {reduced} "
            "measurably reduced pressure at their deployment site."
        )
    return " ".join(parts)


def generate_analytics_report(history: list[dict], deployment_log: list[dict] | None = None) -> dict:
    """Analyze a run's full tick history for bottlenecks, strengths, and suggestions."""
    deployment_log = deployment_log or []
    if not history:
        return {
            "has_data": False,
            "peak_bottlenecks": [],
            "resilient_windows": [],
            "well_buffered_locations": [],
            "suggested_enhancements": [],
            "narrative": "",
            "deployment_impact": [],
        }

    # Track each node's single highest pressure ratio (count / capacity) and
    # how many ticks it spent overloaded, so a brief spike doesn't outrank a
    # sustained bottleneck.
    node_peak_ratio: dict[str, float] = {}
    node_peak_tick: dict[str, int] = {}
    node_peak_day_label: dict[str, str] = {}
    node_overload_tick_count: dict[str, int] = {}
    node_ever_moderate: dict[str, bool] = {}
    resilient_windows = []

    for entry in history:
        location_counts = entry.get("location_counts") or {}
        for node, count in location_counts.items():
            capacity = NODE_CAPACITY_BASELINES.get(node, DEFAULT_NODE_CAPACITY)
            ratio = count / capacity if capacity else 0.0
            if ratio >= 0.5:
                node_ever_moderate[node] = True
            if ratio >= 0.85:
                node_overload_tick_count[node] = node_overload_tick_count.get(node, 0) + 1
            if ratio > node_peak_ratio.get(node, 0.0):
                node_peak_ratio[node] = ratio
                node_peak_tick[node] = entry.get("simulation_tick")
                node_peak_day_label[node] = entry.get("simulation_day_label", "")

        total_agents = entry.get("total_agents", 0)
        if total_agents and entry.get("severity_index", 0.0) < 15 and entry.get("avg_stress", 0.0) < 40:
            resilient_windows.append({
                "tick": entry.get("simulation_tick"),
                "day_label": entry.get("simulation_day_label", ""),
                "severity_index": entry.get("severity_index", 0.0),
            })

    # Only nodes that stayed overloaded for at least two ticks count as a real
    # bottleneck rather than a one-tick blip.
    peak_bottlenecks = [
        {
            "node": node,
            "peak_ratio": round(ratio, 2),
            "peak_tick": node_peak_tick.get(node),
            "peak_day_label": node_peak_day_label.get(node, ""),
            "overload_ticks": node_overload_tick_count.get(node, 0),
        }
        for node, ratio in node_peak_ratio.items()
        if node_overload_tick_count.get(node, 0) >= 2
    ]
    peak_bottlenecks.sort(key=lambda item: item["peak_ratio"], reverse=True)
    peak_bottlenecks = peak_bottlenecks[:5]

    well_buffered_locations = [
        node for node in node_peak_ratio if not node_ever_moderate.get(node)
    ]

    suggested_enhancements = []
    for bottleneck in peak_bottlenecks:
        location_label = bottleneck["node"].replace("_", " ")
        when_label = bottleneck["peak_day_label"] or f"tick {bottleneck['peak_tick']}"
        suggested_enhancements.append(
            f"Add marshals/buses near {location_label} — pressure reached "
            f"{bottleneck['peak_ratio']}x capacity around {when_label}."
        )

    panicking_entries = [entry for entry in history if entry.get("panicking_agents", 0) > 0]
    if panicking_entries:
        worst_entry = max(panicking_entries, key=lambda entry: entry.get("panicking_agents", 0))
        location_label = (worst_entry.get("leading_current_location") or "the affected area").replace("_", " ")
        suggested_enhancements.append(
            f"Increase ambulance coverage near {location_label} — "
            f"{worst_entry.get('panicking_agents')} pilgrim(s) panicking around "
            f"{worst_entry.get('simulation_day_label', '')}."
        )

    for previous_entry, current_entry in zip(history, history[1:]):
        hydration_drop = previous_entry.get("avg_hydration", 100.0) - current_entry.get("avg_hydration", 100.0)
        if hydration_drop >= 8.0:
            suggested_enhancements.append(
                "Add cooling/water stations along the affected corridor — average hydration dropped "
                f"sharply around {current_entry.get('simulation_day_label', '')}."
            )
            break

    if not suggested_enhancements:
        suggested_enhancements.append(
            "No major issues detected in this run — crowd flow stayed within safe thresholds throughout."
        )

    trimmed_resilient_windows = resilient_windows[:5]
    deployment_impact = evaluate_deployment_impact(deployment_log, history)

    narrative = generate_narrative_via_llm(peak_bottlenecks, trimmed_resilient_windows, deployment_impact)
    if narrative is None:
        narrative = _template_narrative(peak_bottlenecks, trimmed_resilient_windows, deployment_impact)

    return {
        "has_data": True,
        "peak_bottlenecks": peak_bottlenecks,
        "resilient_windows": trimmed_resilient_windows,
        "well_buffered_locations": well_buffered_locations,
        "suggested_enhancements": suggested_enhancements,
        "narrative": narrative,
        "deployment_impact": deployment_impact,
    }


# ============================================================
# LLM run logging and the automatic after-action report
# ============================================================

def count_agents_at_risk() -> int:
    """How many pilgrims are currently in a high/severe risk band."""
    return sum(
        1 for agent in REPOSITORY.agents.values()
        if agent.state.risk_level in SIGNIFICANT_RISK_LEVELS
    )


def record_simulation_tick(summary: dict, new_decisions: list) -> None:
    """Append one aggregate row to the simulation log for the tick just run."""
    llm_decisions = sum(1 for record in new_decisions if record.source in {"llm", "cache"})
    SIMULATION_LOG.record_tick(TickRecord(
        tick=summary.get("simulation_tick", 0),
        simulated_time=ENVIRONMENT.to_dict().get("simulated_time_label", ""),
        day_label=summary.get("simulation_day_label", ""),
        current_ritual=summary.get("current_ritual", ""),
        total_agents=summary.get("total_agents", 0),
        severity_index=summary.get("severity_index", 0.0),
        avg_stress=summary.get("avg_stress", 0.0),
        avg_fatigue=summary.get("avg_fatigue", 0.0),
        avg_hydration=summary.get("avg_hydration", 0.0),
        panicking_agents=summary.get("panicking_agents", 0),
        hazard=None if ENVIRONMENT.hazard == "none" else ENVIRONMENT.hazard,
        crowd_density=ENVIRONMENT.density,
        temperature_c=ENVIRONMENT.temperature,
        risks_detected=count_agents_at_risk(),
        decisions_logged=len(new_decisions),
        llm_decisions=llm_decisions,
        fallback_decisions=len(new_decisions) - llm_decisions,
    ))


def build_llm_simulation_report(write_to_disk: bool = False) -> dict:
    """Build the six-section after-action report from the recorded run log."""
    report = build_simulation_report(
        log=SIMULATION_LOG,
        history=SUMMARY_HISTORY,
        llm_status=LLM_ENGINE.status_payload(),
    )
    if write_to_disk and report.get("has_data"):
        stamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
        LAST_REPORT_PATHS.update(write_report(report, REPORTS_DIR, basename=stamp))
        SIMULATION_LOG.write_json(REPORTS_DIR / f"{stamp}_log.json")
        LAST_REPORT_PATHS["log"] = str(REPORTS_DIR / f"{stamp}_log.json")
    report["files"] = dict(LAST_REPORT_PATHS)
    return report


def maybe_finalize_run(summary: dict) -> dict | None:
    """Auto-generate the report the moment the ritual schedule is complete.

    "Hajj Complete" is the same end-of-run signal the dashboard timeline uses,
    so the report lands exactly once, without the operator having to ask.
    """
    if summary.get("current_ritual") != "Hajj Complete":
        return None
    if SIMULATION_LOG.run_completed:
        return None
    SIMULATION_LOG.mark_finished()
    report = build_llm_simulation_report(write_to_disk=True)
    print(f"Simulation complete -- analytical report written to {LAST_REPORT_PATHS.get('markdown')}")
    return report


def reset_llm_run_state() -> None:
    """Clear the decision log, risk events and model counters for a fresh run."""
    SIMULATION_LOG.reset()
    LLM_ENGINE.reset()
    LAST_REPORT_PATHS.clear()


def reset_dashboard_state() -> dict:
    """Reset both environment and agents to the initial loaded project state."""
    ENVIRONMENT.reset()
    REPOSITORY.reset_all()
    sync_hamlah_membership()
    sync_hotel_occupancy()
    DEPLOYMENT_LOG.clear()
    reset_llm_run_state()
    UNIT_REPOSITORY.spawn_default_fleet()
    SUMMARY_HISTORY.clear()
    return update_summary_history()


update_summary_history()


# HTTP layer: routes browser requests to repository/environment operations.
class HajjSimHandler(SimpleHTTPRequestHandler):
    """Request handler that serves both static files and JSON API routes."""

    def __init__(self, *args, **kwargs):
        """Serve frontend files from ``web`` instead of the project root."""
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self) -> None:
        """Disable browser caching so simulation state refreshes immediately."""
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        """Handle dashboard reads: agents, summary, environment, or HTML files."""
        parsed = urlparse(self.path)
        # API reads return JSON snapshots used by app.js during refresh.
        if parsed.path == "/api/agents":
            self._send_json({"agents": REPOSITORY.list_agents()})
            return
        if parsed.path == "/api/summary":
            self._send_json({"summary": build_summary_snapshot(), "history": SUMMARY_HISTORY})
            return
        if parsed.path == "/api/environment":
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return
        if parsed.path == "/api/hamlahs":
            self._send_json({"hamlahs": HAMLAH_REGISTRY.list_hamlahs()})
            return
        if parsed.path == "/api/hotels":
            self._send_json({"hotels": HOTEL_REGISTRY.list_hotels()})
            return
        if parsed.path == "/api/units":
            self._send_json({"units": UNIT_REPOSITORY.list_units()})
            return
        if parsed.path == "/api/analytics/report":
            self._send_json({"report": generate_analytics_report(SUMMARY_HISTORY, DEPLOYMENT_LOG)})
            return
        if parsed.path == "/api/llm/status":
            # Configuration + live counters; never exposes the API key itself.
            self._send_json({"llm": LLM_ENGINE.status_payload(), "llm_agent_ids": sorted(LLM_AGENT_IDS)})
            return
        if parsed.path == "/api/logs/decisions":
            limit = int((parse_qs(parsed.query).get("limit") or ["200"])[0])
            records = SIMULATION_LOG.decisions[-max(1, min(2000, limit)):]
            self._send_json({
                "decisions": [record.to_payload() for record in records],
                "total": len(SIMULATION_LOG.decisions),
            })
            return
        if parsed.path == "/api/logs/risks":
            self._send_json({
                "risk_events": [event.to_payload() for event in SIMULATION_LOG.risk_events],
                "total": len(SIMULATION_LOG.risk_events),
            })
            return
        if parsed.path == "/api/logs/simulation":
            self._send_json({"log": SIMULATION_LOG.to_payload()})
            return
        if parsed.path == "/api/analytics/simulation-report":
            # Read-only: the report the run has produced so far.
            self._send_json({"report": build_llm_simulation_report(write_to_disk=False)})
            return
        if parsed.path == "/api/analytics/simulation-report.md":
            # Same report as Markdown, for copy/paste into a write-up.
            markdown = render_markdown(build_llm_simulation_report(write_to_disk=False))
            body = markdown.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path in ("/", "/index.html"):
            # The root URL serves the dashboard HTML from the web directory.
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        """Handle dashboard writes: create agents, step simulation, or reset."""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else ""
        payload = self._parse_body(raw_body)

        if parsed.path == "/api/agents":
            # Add one manually configured pilgrim to the current roster.
            try:
                snapshot = REPOSITORY.create_manual_agent(payload, HAMLAH_REGISTRY)
            except ValueError as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
                return
            sync_hamlah_membership()
            update_summary_history()
            self._send_json({"agent": snapshot}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/agents/random":
            # Add a bounded batch of generated pilgrims to avoid huge UI payloads.
            count = max(1, min(500, int(payload.get("count", 10))))
            agents = REPOSITORY.generate_random_agents(count, HAMLAH_REGISTRY.nationality_to_hamlah_id())
            sync_hamlah_membership()
            update_summary_history()
            self._send_json({"agents": agents}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/units/deploy":
            # Manually click-to-place one police/marshal/ambulance unit.
            try:
                unit_snapshot = UNIT_REPOSITORY.deploy_unit(payload.get("unit_type", ""), payload.get("node_id", ""))
            except ValueError as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
                return
            DEPLOYMENT_LOG.append({
                "tick": ENVIRONMENT.tick + 1,
                "unit_id": unit_snapshot["unit_id"],
                "unit_type": unit_snapshot["unit_type"],
                "node_id": unit_snapshot["current_node"],
            })
            self._send_json({"unit": unit_snapshot}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/environment":
            # Update sliders/dropdowns without advancing the ritual tick.
            ENVIRONMENT.apply_updates(payload)
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return

        if parsed.path == "/api/simulate/step":
            # Run one perceive-decide-act cycle for every active pilgrim, let
            # the convoy coordinator move corridor buses and board/disembark
            # cohorts, then let marshal/police/ambulance/legacy-bus units
            # react to the same environment/pilgrim state.
            ENVIRONMENT.apply_updates(payload)
            environment_payload = ENVIRONMENT.to_payload()
            environment_payload["hamlah_hotel_map"] = build_hamlah_hotel_map()
            # Reset the model's per-tick call budget and refresh which pilgrims
            # it drives, then log everything this tick produces.
            LLM_ENGINE.begin_tick(ENVIRONMENT.tick + 1)
            refresh_llm_agent_selection(REPOSITORY.agents.keys())
            decisions_before = len(SIMULATION_LOG.decisions)
            actions = REPOSITORY.step_all(
                environment_payload,
                HAMLAH_REGISTRY.get_dispatch_offsets(),
                post_step_hook=finalize_agent_decision,
            )
            CONVOY_COORDINATOR.step(REPOSITORY.agents, UNIT_REPOSITORY.units, ENVIRONMENT.tick + 1)
            UNIT_REPOSITORY.step_all(environment_payload, REPOSITORY.list_agents())
            sync_hotel_occupancy()
            ENVIRONMENT.tick += 1
            summary = update_summary_history()
            new_decisions = SIMULATION_LOG.decisions[decisions_before:]
            record_simulation_tick(summary, new_decisions)
            auto_report = maybe_finalize_run(summary)
            self._send_json(
                {
                    "environment": ENVIRONMENT.to_dict(),
                    "actions": actions,
                    "summary": summary,
                    "history": SUMMARY_HISTORY,
                    "llm": LLM_ENGINE.status_payload(),
                    "llm_decisions": [record.to_payload() for record in new_decisions],
                    "simulation_report": auto_report,
                }
            )
            return

        if parsed.path == "/api/simulate/reset":
            # Restart the ritual timeline but keep manually/generated agents.
            # Units are also respawned fresh -- otherwise a bus's passenger
            # manifest could still reference pilgrim ids that reset_ritual_days
            # just snapped back to PEDESTRIAN at their start node.
            ENVIRONMENT.reset()
            REPOSITORY.reset_ritual_days()
            UNIT_REPOSITORY.spawn_default_fleet()
            sync_hotel_occupancy()
            DEPLOYMENT_LOG.clear()
            reset_llm_run_state()
            summary = update_summary_history()
            self._send_json(
                {
                    "environment": ENVIRONMENT.to_dict(),
                    "summary": summary,
                    "history": SUMMARY_HISTORY,
                }
            )
            return

        if parsed.path == "/api/analytics/simulation-report":
            # Force-generate the after-action report and write it to reports/.
            report = build_llm_simulation_report(write_to_disk=True)
            self._send_json({"report": report, "files": report.get("files", {})})
            return

        if parsed.path == "/api/llm/reload":
            # Re-read LLM_* environment variables without restarting the server.
            LLM_ENGINE.reload_settings()
            refresh_llm_agent_selection(REPOSITORY.agents.keys())
            self._send_json({"llm": LLM_ENGINE.status_payload()})
            return

        if parsed.path == "/api/dashboard/reset":
            # Return the entire dashboard to the original file-backed state.
            summary = reset_dashboard_state()
            self._send_json(
                {
                    "agents": REPOSITORY.list_agents(),
                    "environment": ENVIRONMENT.to_dict(),
                    "summary": summary,
                    "history": SUMMARY_HISTORY,
                }
            )
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def _parse_body(self, raw_body: str) -> dict:
        """Read JSON or URL-encoded form bodies into a normal dictionary."""
        content_type = self.headers.get("Content-Type", "")
        # The JavaScript client sends JSON, but URL-encoded parsing keeps the
        # handler flexible for simple manual form/API testing.
        if "application/json" in content_type:
            return json.loads(raw_body or "{}")
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(raw_body)
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
        return {}

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        """Serialize a Python dictionary as an HTTP JSON response."""
        # JSON responses use explicit length and UTF-8 headers for browser
        # compatibility with the static frontend.
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def warn_if_key_in_template() -> bool:
    """Shout if a real-looking key has been put in the COMMITTED .env.example.

    .env.example is a documentation template that ships in the repository, so a
    key placed there gets published the moment anyone pushes. .env is the
    git-ignored file that is actually read. These two are easy to confuse, and
    the mistake is silent until it is public -- so check for it out loud on
    every boot.
    """
    template = BASE_DIR / ".env.example"
    if not template.is_file():
        return False
    key_shapes = re.compile(r"AIza[0-9A-Za-z_-]{30,}|AQ\.[0-9A-Za-z_-]{30,}|sk-ant-[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z]{32,}")
    try:
        contents = template.read_text(encoding="utf-8")
    except OSError:
        return False
    if not key_shapes.search(contents):
        return False
    print("")
    print("!" * 74)
    print("!! WARNING: .env.example appears to contain a REAL API key.")
    print("!! .env.example is COMMITTED to the repository -- pushing it publishes")
    print("!! the key. Move it to .env (git-ignored) and restore the placeholder:")
    print("!!     LLM_API_KEY=paste-your-key-here")
    print("!" * 74)
    print("")
    return True


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the threaded local web server used during demos/development."""
    server = ThreadingHTTPServer((host, port), HajjSimHandler)
    print(f"HajjSim web app running at http://{host}:{port}")
    warn_if_key_in_template()
    # Startup diagnostics for the decision layer -- names only, never values.
    if _LOADED_ENV_VARS:
        print(f"Loaded {_LOADED_ENV_VARS} variable(s) from {ENV_FILE.name}")
    status = LLM_ENGINE.status_payload()
    if status["active"]:
        print(
            f"LLM decisions ACTIVE -- provider={status['provider']} model={status['model']} "
            f"driving={'all pilgrims' if status['max_agents'] == 0 else str(status['max_agents']) + ' pilgrim(s)'}"
        )
    else:
        reason = "LLM_ENABLED is off" if not status["enabled"] else (
            "no LLM_API_KEY found" if not status["api_key_present"] else
            f"unknown LLM_PROVIDER {status['provider']!r}"
        )
        print(f"LLM decisions INACTIVE ({reason}) -- agents will use the rule-based engine")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
