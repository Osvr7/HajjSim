"""HTTP backend for the HajjSim dashboard.

This module serves the static web dashboard from the ``web`` folder and exposes
small JSON API endpoints that the frontend uses to create agents, update the
environment, advance the simulation, and read operational metrics.
"""

import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from hajj_agents import (
    AgentFactory,
    build_agent_from_record,
    build_manual_agent,
    get_simulation_day_payload,
    get_simulation_tick_payload,
    get_ritual_schedule_payload,
)


# Project paths used by both the static file server and the API layer.
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web"
DATA_FILE = BASE_DIR / "pilgrims.json"


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
        if "density" in payload:
            self.density = max(0.0, min(10.0, float(payload["density"])))
        if "temperature" in payload:
            self.temperature = max(20.0, min(50.0, float(payload["temperature"])))
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
        }

    def to_dict(self) -> dict:
        """Build the JSON-safe environment object returned to the frontend."""
        tick_state = self._current_tick_state()
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
        if not self.data_file.exists():
            self.agents = {}
            self._next_index = 1
            return

        with self.data_file.open("r", encoding="utf-8") as file:
            records = json.load(file)

        self.agents = {}
        max_index = 0
        for record in records:
            agent = build_agent_from_record(record)
            self.agents[agent.profile.pilgrim_id] = agent
            digits = "".join(char for char in agent.profile.pilgrim_id if char.isdigit())
            if digits:
                max_index = max(max_index, int(digits))
        self._next_index = max_index + 1 if max_index else 1

    def list_agents(self) -> list[dict]:
        """Return frontend-ready snapshots for all active agents."""
        return [agent.get_snapshot() for agent in self.agents.values()]

    def create_manual_agent(self, payload: dict) -> dict:
        """Create one agent from the manual dashboard form."""
        pilgrim_id = payload.get("pilgrim_id") or f"P_{self._next_index:04d}"
        chronic_conditions = self._parse_conditions(payload.get("chronic_conditions", []))

        agent = build_manual_agent(
            pilgrim_id=pilgrim_id,
            age=int(payload["age"]),
            nationality=payload["nationality"],
            group_id=payload["group_id"],
            mobility=float(payload["mobility"]),
            health_status=payload["health_status"],
            initial_node=payload["initial_node"],
            target_node=payload["target_node"],
            language=payload.get("language", "Arabic"),
            chronic_conditions=chronic_conditions,
            risk_tolerance=float(payload.get("risk_tolerance", 0.5)),
            performs_sacrifice=self._parse_bool(payload.get("performs_sacrifice", True)),
        )
        self.agents[agent.profile.pilgrim_id] = agent
        self._advance_index(agent.profile.pilgrim_id)
        return agent.get_snapshot()

    def generate_random_agents(self, count: int) -> list[dict]:
        """Generate a synthetic population using demographic distributions."""
        generated = self.factory.generate_agents(count=count, start_index=self._next_index)
        self.agents.update(generated)
        self._next_index += count
        return [agent.get_snapshot() for agent in generated.values()]

    def step_all(self, environment_data: dict) -> list[dict]:
        """Advance every agent once and return the action each agent selected."""
        group_locations = {}
        for agent in self.agents.values():
            group_locations.setdefault(agent.profile.group_id, []).append(agent.state.current_node)

        step_environment = dict(environment_data)
        step_environment["group_locations"] = group_locations

        actions = []
        for agent in self.agents.values():
            action = agent.step(step_environment)
            actions.append({"pilgrim_id": agent.profile.pilgrim_id, "action": action})
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


def derive_operational_status(agent: dict) -> str:
    """Classify a pilgrim into the status color shown on the dashboard."""
    state = agent.get("state", {})
    stress = float(state.get("stress", 0))
    fatigue = float(state.get("fatigue", 0))
    hydration = float(state.get("hydration", 100))

    if state.get("is_panicking"):
        return "panicking"
    if stress >= 88 or fatigue >= 86 or hydration <= 28:
        return "high_risk"
    if stress >= 62 or fatigue >= 58 or hydration <= 62:
        return "needs_support"
    return "stable"


# Global simulation session state used by the HTTP handler.
REPOSITORY = AgentRepository(DATA_FILE)
ENVIRONMENT = EnvironmentState()
SUMMARY_HISTORY: list[dict] = []


def build_summary_snapshot() -> dict:
    """Aggregate all agents into the top-level operational dashboard metrics."""
    agents = REPOSITORY.list_agents()
    total = len(agents)
    stable = 0
    needs_support = 0
    high_risk = 0
    panicking = 0
    location_counts = {}

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

    avg_stress = round(sum(agent["state"]["stress"] for agent in agents) / total, 1) if total else 0.0
    avg_fatigue = round(sum(agent["state"]["fatigue"] for agent in agents) / total, 1) if total else 0.0
    avg_hydration = round(sum(agent["state"]["hydration"] for agent in agents) / total, 1) if total else 0.0
    severity_index = round(
        ((panicking * 1.0) + (high_risk * 0.7) + (needs_support * 0.4)) / total * 100,
        1,
    ) if total else 0.0

    leading_current_location = None
    if location_counts:
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
    }


def update_summary_history() -> dict:
    """Store one summary point per ritual tick for the line chart."""
    summary = build_summary_snapshot()
    entry = {**summary}
    if SUMMARY_HISTORY and SUMMARY_HISTORY[-1]["simulation_tick"] == entry["simulation_tick"]:
        SUMMARY_HISTORY[-1] = entry
    else:
        SUMMARY_HISTORY.append(entry)
    return summary


def reset_dashboard_state() -> dict:
    """Reset both environment and agents to the initial loaded project state."""
    ENVIRONMENT.reset()
    REPOSITORY.reset_all()
    SUMMARY_HISTORY.clear()
    return update_summary_history()


update_summary_history()


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
        if parsed.path == "/api/agents":
            self._send_json({"agents": REPOSITORY.list_agents()})
            return
        if parsed.path == "/api/summary":
            self._send_json({"summary": build_summary_snapshot(), "history": SUMMARY_HISTORY})
            return
        if parsed.path == "/api/environment":
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return
        if parsed.path in ("/", "/index.html"):
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
            snapshot = REPOSITORY.create_manual_agent(payload)
            update_summary_history()
            self._send_json({"agent": snapshot}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/agents/random":
            # Add a bounded batch of generated pilgrims to avoid huge UI payloads.
            count = max(1, min(500, int(payload.get("count", 10))))
            agents = REPOSITORY.generate_random_agents(count)
            update_summary_history()
            self._send_json({"agents": agents}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/environment":
            # Update sliders/dropdowns without advancing the ritual tick.
            ENVIRONMENT.apply_updates(payload)
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return

        if parsed.path == "/api/simulate/step":
            # Run one perceive-decide-act cycle for every active pilgrim.
            ENVIRONMENT.apply_updates(payload)
            actions = REPOSITORY.step_all(ENVIRONMENT.to_payload())
            ENVIRONMENT.tick += 1
            summary = update_summary_history()
            self._send_json(
                {
                    "environment": ENVIRONMENT.to_dict(),
                    "actions": actions,
                    "summary": summary,
                    "history": SUMMARY_HISTORY,
                }
            )
            return

        if parsed.path == "/api/simulate/reset":
            # Restart the ritual timeline but keep manually/generated agents.
            ENVIRONMENT.reset()
            REPOSITORY.reset_ritual_days()
            summary = update_summary_history()
            self._send_json(
                {
                    "environment": ENVIRONMENT.to_dict(),
                    "summary": summary,
                    "history": SUMMARY_HISTORY,
                }
            )
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
        if "application/json" in content_type:
            return json.loads(raw_body or "{}")
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(raw_body)
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
        return {}

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        """Serialize a Python dictionary as an HTTP JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the threaded local web server used during demos/development."""
    server = ThreadingHTTPServer((host, port), HajjSimHandler)
    print(f"HajjSim web app running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
