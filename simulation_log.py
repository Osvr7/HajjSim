"""Structured logging of LLM decisions, risk events and per-tick state.

The after-action report must be built from what actually happened during a run,
not from assumptions, so every decision the LLM layer makes and every
significant risk a pilgrim enters is recorded here as it happens.

Three record types
------------------
* :class:`DecisionRecord` -- one per LLM-eligible decision: the environment the
  model saw, the options it was given, what it picked, why, and what the world
  looked like immediately after the action executed.
* :class:`RiskEvent` -- a *lifecycle*, not a point in time. It opens when a
  pilgrim crosses into a high/severe risk band, accumulates the decisions taken
  while it is open, and closes with an outcome verdict (avoided / reduced /
  unchanged / worsened) derived from the risk score at open versus at close.
* :class:`TickRecord` -- one aggregate row per simulation tick, so the report
  can describe the run's shape without replaying every agent.

The log is thread-safe (the dashboard runs a ``ThreadingHTTPServer``) and
bounded, so a long run cannot exhaust memory.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# Hard caps: a 240-tick run with a wide agent sample stays well inside these.
MAX_DECISION_RECORDS = 20000
MAX_RISK_EVENTS = 4000
MAX_TICK_RECORDS = 2000


@dataclass
class DecisionRecord:
    """One decision step: what was observed, what was offered, what was chosen."""

    tick: int
    simulated_time: str
    pilgrim_id: str

    # -- what the agent saw -------------------------------------------------
    location: str
    zone: str
    target_node: str
    risk_level: str
    risk_score: float
    risk_factors: List[str] = field(default_factory=list)
    hazard: Optional[str] = None
    crowd_density: float = 0.0
    temperature_c: float = 0.0
    congestion_ratio: float = 0.0

    # -- what it could do and what it did -----------------------------------
    available_actions: List[str] = field(default_factory=list)
    action: str = ""
    # stay | rest | advance | reroute | avoid | regroup | drift | emergency | locked
    action_kind: str = ""
    # Hops from the pilgrim's node to its ritual target at decision time; the
    # report compares this across consecutive decisions to measure whether the
    # agent is actually making progress.
    distance_hops: int = 0
    reason: str = ""
    source: str = ""
    fallback_action: str = ""
    error: str = ""
    latency_ms: int = 0
    provider: str = ""
    model: str = ""

    # -- what happened as a result (filled in after execution) --------------
    resulting_node: str = ""
    moved: bool = False
    risk_level_after: str = ""
    risk_score_after: float = 0.0
    stress_delta: float = 0.0
    hydration_delta: float = 0.0
    fatigue_delta: float = 0.0
    executed: bool = False

    # -- internal: vitals captured before execution, used for the deltas ----
    _stress_before: float = 0.0
    _fatigue_before: float = 0.0
    _hydration_before: float = 0.0

    def to_payload(self) -> dict:
        """JSON-safe form (drops the private pre-execution scratch fields)."""
        return {key: value for key, value in asdict(self).items() if not key.startswith("_")}


@dataclass
class RiskEvent:
    """A period during which one pilgrim was in a high or severe risk band."""

    event_id: str
    pilgrim_id: str
    opened_tick: int
    opened_time: str
    location: str
    risk_type: str
    opened_level: str
    opened_score: float
    trigger_factors: List[str] = field(default_factory=list)
    environment: Dict[str, object] = field(default_factory=dict)

    peak_level: str = ""
    peak_score: float = 0.0
    peak_tick: int = 0

    decisions: List[dict] = field(default_factory=list)

    closed_tick: Optional[int] = None
    closed_time: str = ""
    closed_level: str = ""
    closed_score: float = 0.0
    closed_location: str = ""
    duration_ticks: int = 0
    outcome: str = "active"
    outcome_detail: str = ""

    def to_payload(self) -> dict:
        """JSON-safe form of the whole event lifecycle."""
        return asdict(self)


@dataclass
class TickRecord:
    """Aggregate state for one simulation tick."""

    tick: int
    simulated_time: str = ""
    day_label: str = ""
    current_ritual: str = ""
    total_agents: int = 0
    severity_index: float = 0.0
    avg_stress: float = 0.0
    avg_fatigue: float = 0.0
    avg_hydration: float = 0.0
    panicking_agents: int = 0
    hazard: Optional[str] = None
    crowd_density: float = 0.0
    temperature_c: float = 0.0
    risks_detected: int = 0
    decisions_logged: int = 0
    llm_decisions: int = 0
    fallback_decisions: int = 0

    def to_payload(self) -> dict:
        """JSON-safe form."""
        return asdict(self)


class SimulationLog:
    """Thread-safe store of decisions, risk-event lifecycles and tick rows."""

    def __init__(self):
        self._lock = threading.RLock()
        self.decisions: List[DecisionRecord] = []
        self.risk_events: List[RiskEvent] = []
        self.ticks: List[TickRecord] = []
        # pilgrim_id -> the risk event currently open for that pilgrim
        self._open_risks: Dict[str, RiskEvent] = {}
        # pilgrim_id -> decision awaiting its post-execution outcome
        self._pending: Dict[str, DecisionRecord] = {}
        self._event_counter = 0
        self.started_at: float = time.time()
        self.finished_at: Optional[float] = None
        self.run_completed: bool = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Clear everything for a fresh run."""
        with self._lock:
            self.decisions.clear()
            self.risk_events.clear()
            self.ticks.clear()
            self._open_risks.clear()
            self._pending.clear()
            self._event_counter = 0
            self.started_at = time.time()
            self.finished_at = None
            self.run_completed = False

    def mark_finished(self) -> None:
        """Mark the run complete and close any still-open risk events."""
        with self._lock:
            if self.run_completed:
                return
            self.run_completed = True
            self.finished_at = time.time()
            for event in list(self._open_risks.values()):
                event.outcome = "unresolved"
                event.outcome_detail = "Still in a high-risk band when the simulation ended."
                event.duration_ticks = max(1, (self.ticks[-1].tick if self.ticks else event.opened_tick) - event.opened_tick + 1)
            self._open_risks.clear()

    @property
    def has_data(self) -> bool:
        """True when anything at all was recorded."""
        with self._lock:
            return bool(self.decisions or self.risk_events or self.ticks)

    # ------------------------------------------------------------------
    # Decisions
    # ------------------------------------------------------------------
    def open_decision(self, record: DecisionRecord) -> None:
        """Record a decision that has been made but not yet executed."""
        with self._lock:
            self._pending[record.pilgrim_id] = record
            open_event = self._open_risks.get(record.pilgrim_id)
            if open_event is not None:
                open_event.decisions.append({
                    "tick": record.tick,
                    "action": record.action,
                    "reason": record.reason,
                    "source": record.source,
                    "risk_level": record.risk_level,
                    "risk_score": record.risk_score,
                })

    def close_decision(
        self,
        pilgrim_id: str,
        resulting_node: str,
        risk_level_after: str,
        risk_score_after: float,
        stress_after: float,
        fatigue_after: float,
        hydration_after: float,
    ) -> Optional[DecisionRecord]:
        """Attach the post-execution result to this pilgrim's pending decision."""
        with self._lock:
            record = self._pending.pop(pilgrim_id, None)
            if record is None:
                return None
            record.resulting_node = resulting_node
            record.moved = resulting_node != record.location
            record.risk_level_after = risk_level_after
            record.risk_score_after = round(risk_score_after, 1)
            record.stress_delta = round(stress_after - record._stress_before, 1)
            record.fatigue_delta = round(fatigue_after - record._fatigue_before, 1)
            record.hydration_delta = round(hydration_after - record._hydration_before, 1)
            record.executed = True
            self.decisions.append(record)
            if len(self.decisions) > MAX_DECISION_RECORDS:
                del self.decisions[: len(self.decisions) - MAX_DECISION_RECORDS]
            return record

    # ------------------------------------------------------------------
    # Risk events
    # ------------------------------------------------------------------
    def observe_risk(
        self,
        pilgrim_id: str,
        tick: int,
        simulated_time: str,
        location: str,
        risk: dict,
        environment: dict,
        significant_levels: frozenset = frozenset({"high", "severe"}),
    ) -> Optional[RiskEvent]:
        """Open, update or close this pilgrim's risk event for the current tick.

        Called once per tick per tracked pilgrim, straight after perception.
        Returns the event that is open afterwards, or None when the pilgrim is
        not currently in a significant-risk band.
        """
        level = str(risk.get("level", "none"))
        score = float(risk.get("score", 0.0))
        with self._lock:
            open_event = self._open_risks.get(pilgrim_id)

            if level in significant_levels:
                if open_event is None:
                    self._event_counter += 1
                    open_event = RiskEvent(
                        event_id=f"RISK_{self._event_counter:05d}",
                        pilgrim_id=pilgrim_id,
                        opened_tick=tick,
                        opened_time=simulated_time,
                        location=location,
                        risk_type=self._classify_risk_type(risk),
                        opened_level=level,
                        opened_score=round(score, 1),
                        trigger_factors=list(risk.get("factors", [])),
                        environment=dict(environment),
                        peak_level=level,
                        peak_score=round(score, 1),
                        peak_tick=tick,
                    )
                    self.risk_events.append(open_event)
                    if len(self.risk_events) > MAX_RISK_EVENTS:
                        del self.risk_events[: len(self.risk_events) - MAX_RISK_EVENTS]
                    self._open_risks[pilgrim_id] = open_event
                elif score > open_event.peak_score:
                    open_event.peak_score = round(score, 1)
                    open_event.peak_level = level
                    open_event.peak_tick = tick
                return open_event

            if open_event is not None:
                self._close_risk(open_event, tick, simulated_time, location, level, score)
                self._open_risks.pop(pilgrim_id, None)
            return None

    def _close_risk(
        self,
        event: RiskEvent,
        tick: int,
        simulated_time: str,
        location: str,
        level: str,
        score: float,
    ) -> None:
        """Close a risk event and judge whether the decisions taken helped."""
        event.closed_tick = tick
        event.closed_time = simulated_time
        event.closed_level = level
        event.closed_score = round(score, 1)
        event.closed_location = location
        event.duration_ticks = max(1, tick - event.opened_tick)

        opened = event.opened_score or 1.0
        if score <= opened * 0.6:
            event.outcome = "avoided"
            event.outcome_detail = (
                f"Risk fell from {event.opened_score} to {event.closed_score} over "
                f"{event.duration_ticks} tick(s); the pilgrim left the danger band decisively."
            )
        elif score < opened:
            event.outcome = "reduced"
            event.outcome_detail = (
                f"Risk eased from {event.opened_score} to {event.closed_score}, but only partially."
            )
        elif score > opened * 1.15:
            event.outcome = "worsened"
            event.outcome_detail = (
                f"Risk rose from {event.opened_score} to {event.closed_score} before the band cleared."
            )
        else:
            event.outcome = "unchanged"
            event.outcome_detail = (
                f"Risk score barely moved ({event.opened_score} -> {event.closed_score})."
            )

    @staticmethod
    def _classify_risk_type(risk: dict) -> str:
        """Name the dominant driver of a risk so events can be grouped."""
        hazard = risk.get("hazard")
        if hazard:
            return str(hazard)
        factors = risk.get("factors") or []
        for keyword, label in (
            ("panicking", "panic"),
            ("dehydration", "dehydration"),
            ("hydration", "dehydration"),
            ("stress", "psychological_stress"),
            ("fatigue", "exhaustion"),
            ("capacity", "overcrowding"),
            ("congested", "overcrowding"),
            ("density", "overcrowding"),
            ("heat", "heat_exposure"),
            ("separated", "group_separation"),
        ):
            for factor in factors:
                if keyword in str(factor).lower():
                    return label
        return "compound_risk"

    # ------------------------------------------------------------------
    # Ticks
    # ------------------------------------------------------------------
    def record_tick(self, record: TickRecord) -> None:
        """Append one aggregate row for a completed simulation tick."""
        with self._lock:
            self.ticks.append(record)
            if len(self.ticks) > MAX_TICK_RECORDS:
                del self.ticks[: len(self.ticks) - MAX_TICK_RECORDS]

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def to_payload(self, decision_limit: int = 500, risk_limit: int = 200) -> dict:
        """Return a trimmed JSON-safe view for the API/dashboard."""
        with self._lock:
            return {
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "run_completed": self.run_completed,
                "counts": {
                    "decisions": len(self.decisions),
                    "risk_events": len(self.risk_events),
                    "ticks": len(self.ticks),
                    "open_risk_events": len(self._open_risks),
                },
                "decisions": [record.to_payload() for record in self.decisions[-decision_limit:]],
                "risk_events": [event.to_payload() for event in self.risk_events[-risk_limit:]],
                "ticks": [record.to_payload() for record in self.ticks],
            }

    def write_json(self, path: Path) -> Path:
        """Write the complete raw log to disk for offline analysis."""
        with self._lock:
            payload = {
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "run_completed": self.run_completed,
                "decisions": [record.to_payload() for record in self.decisions],
                "risk_events": [event.to_payload() for event in self.risk_events],
                "ticks": [record.to_payload() for record in self.ticks],
            }
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, default=str)
        return path
