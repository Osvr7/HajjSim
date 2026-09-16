"""After-action analytical report for an LLM-driven HajjSim run.

Everything in here is computed from :class:`simulation_log.SimulationLog` --
the decisions the model actually made, the risk events that actually opened,
and the per-tick aggregates that were actually recorded. Nothing is inferred
from the plan or assumed from the configuration, so a claim in the report can
always be traced back to a logged row.

The report is produced in two forms from the same data:
* :func:`build_simulation_report` -- a nested dict for the API/dashboard.
* :func:`render_markdown` -- a human-readable file written to ``reports/``.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from simulation_log import SimulationLog

# One tick of simulated time, kept in sync with the agent engine.
from hajj_agents import SIMULATED_MINUTES_PER_TICK

# Action kinds that represent a deliberate protective response to danger.
PROTECTIVE_KINDS = {"rest", "avoid", "emergency", "reroute", "stay"}
# Action kinds that change the pilgrim's road/path away from the planned route.
ROUTE_CHANGE_KINDS = {"reroute", "avoid", "regroup", "drift"}


def _round(value: float, digits: int = 1) -> float:
    """Round defensively -- report maths should never raise."""
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return 0.0


def _percent(part: int, whole: int) -> float:
    """Percentage helper that tolerates an empty denominator."""
    return _round((part / whole) * 100.0) if whole else 0.0


# ============================================================
# Section 1 -- Simulation overview
# ============================================================

def _build_overview(log: SimulationLog, history: List[dict]) -> dict:
    """Total duration, decision steps, movements and risks detected."""
    ticks = log.ticks
    tick_count = len(ticks)
    last_tick = ticks[-1].tick if ticks else (history[-1].get("simulation_tick", 0) if history else 0)
    simulated_minutes = tick_count * SIMULATED_MINUTES_PER_TICK
    wall_clock = (log.finished_at or time.time()) - log.started_at

    decisions = log.decisions
    movements = sum(1 for record in decisions if record.moved)
    llm_decisions = sum(1 for record in decisions if record.source in {"llm", "cache"})

    return {
        "ticks_recorded": tick_count,
        "final_tick": last_tick,
        "simulated_minutes": simulated_minutes,
        "simulated_hours": _round(simulated_minutes / 60.0),
        "simulated_days": _round(simulated_minutes / (60.0 * 24.0), 2),
        "minutes_per_tick": SIMULATED_MINUTES_PER_TICK,
        "wall_clock_seconds": _round(wall_clock),
        "decision_steps": len(decisions),
        "llm_decision_steps": llm_decisions,
        "fallback_decision_steps": len(decisions) - llm_decisions,
        "llm_share_percent": _percent(llm_decisions, len(decisions)),
        "movements": movements,
        "movement_share_percent": _percent(movements, len(decisions)),
        "risk_events_detected": len(log.risk_events),
        "risk_detections_per_tick": _round(sum(record.risks_detected for record in ticks) / tick_count) if tick_count else 0.0,
        "agents_at_end": ticks[-1].total_agents if ticks else 0,
        "run_completed": log.run_completed,
    }


# ============================================================
# Section 2 -- Decision analysis
# ============================================================

def _build_decision_analysis(log: SimulationLog) -> dict:
    """Action frequencies, key decision points, and worked examples."""
    decisions = log.decisions
    if not decisions:
        return {
            "action_counts": [],
            "kind_counts": [],
            "source_counts": [],
            "key_decision_points": [],
            "successful_examples": [],
            "unsuccessful_examples": [],
            "avg_latency_ms": 0.0,
            "invalid_or_failed": 0,
        }

    action_counter = Counter(record.action for record in decisions)
    kind_counter = Counter(record.action_kind or "unclassified" for record in decisions)
    source_counter = Counter(record.source for record in decisions)

    total = len(decisions)
    action_counts = [
        {"action": action, "count": count, "share_percent": _percent(count, total)}
        for action, count in action_counter.most_common()
    ]
    kind_counts = [
        {"kind": kind, "count": count, "share_percent": _percent(count, total)}
        for kind, count in kind_counter.most_common()
    ]
    source_counts = [
        {"source": source, "count": count, "share_percent": _percent(count, total)}
        for source, count in source_counter.most_common()
    ]

    # A decision "matters" when the pilgrim was already in danger and had a
    # real choice to make: those are the moments worth reading.
    key_points = [
        record for record in decisions
        if record.risk_level in {"high", "severe"} and len(record.available_actions) > 2
    ]
    key_points.sort(key=lambda record: record.risk_score, reverse=True)

    # Effectiveness: did the risk score actually fall after the action ran?
    scored = [record for record in decisions if record.executed and record.risk_level in {"moderate", "high", "severe"}]
    improved = sorted(scored, key=lambda record: record.risk_score_after - record.risk_score)
    worsened = sorted(scored, key=lambda record: record.risk_score - record.risk_score_after)

    latencies = [record.latency_ms for record in decisions if record.latency_ms > 0]
    invalid_or_failed = sum(1 for record in decisions if record.source.startswith("fallback"))

    return {
        "action_counts": action_counts,
        "kind_counts": kind_counts,
        "source_counts": source_counts,
        "distinct_actions_used": len(action_counter),
        "key_decision_points": [_decision_summary(record) for record in key_points[:10]],
        "successful_examples": [_decision_summary(record) for record in improved[:5] if record.risk_score_after < record.risk_score],
        "unsuccessful_examples": [_decision_summary(record) for record in worsened[:5] if record.risk_score_after > record.risk_score],
        "avg_latency_ms": _round(sum(latencies) / len(latencies)) if latencies else 0.0,
        "invalid_or_failed": invalid_or_failed,
    }


def _decision_summary(record) -> dict:
    """Compact, readable form of one decision for the report."""
    return {
        "tick": record.tick,
        "simulated_time": record.simulated_time,
        "pilgrim_id": record.pilgrim_id,
        "location": record.location,
        "risk_level": record.risk_level,
        "risk_score": record.risk_score,
        "risk_score_after": record.risk_score_after,
        "hazard": record.hazard,
        "options_offered": len(record.available_actions),
        "action": record.action,
        "action_kind": record.action_kind,
        "reason": record.reason,
        "source": record.source,
        "resulting_node": record.resulting_node,
        "moved": record.moved,
        "risk_delta": _round(record.risk_score_after - record.risk_score),
    }


# ============================================================
# Section 3 -- Risk analysis
# ============================================================

def _build_risk_analysis(log: SimulationLog) -> dict:
    """Per-event detail plus outcome and risk-type distributions."""
    events = log.risk_events
    if not events:
        return {
            "total_events": 0,
            "outcome_counts": [],
            "risk_type_counts": [],
            "significant_events": [],
            "worst_event": None,
        }

    outcome_counter = Counter(event.outcome for event in events)
    type_counter = Counter(event.risk_type for event in events)

    ranked = sorted(events, key=lambda event: (event.peak_score, event.duration_ticks), reverse=True)
    significant = [_risk_event_detail(event) for event in ranked[:10]]

    return {
        "total_events": len(events),
        "outcome_counts": [
            {"outcome": outcome, "count": count, "share_percent": _percent(count, len(events))}
            for outcome, count in outcome_counter.most_common()
        ],
        "risk_type_counts": [
            {"risk_type": risk_type, "count": count, "share_percent": _percent(count, len(events))}
            for risk_type, count in type_counter.most_common()
        ],
        "significant_events": significant,
        "worst_event": significant[0] if significant else None,
        "avg_duration_ticks": _round(sum(event.duration_ticks for event in events) / len(events)),
    }


def _risk_event_detail(event) -> dict:
    """Answer the six report questions for one risk event."""
    environment = event.environment or {}
    decisions = event.decisions or []
    first_protective = next(
        (decision for decision in decisions if decision.get("action") in {"REST", "AVOID_CROWD", "ENTER_PANIC_MODE"}
         or str(decision.get("action", "")).startswith("MOVE_TO_")),
        None,
    )
    return {
        "event_id": event.event_id,
        "pilgrim_id": event.pilgrim_id,
        # When
        "opened_tick": event.opened_tick,
        "opened_time": event.opened_time,
        "closed_tick": event.closed_tick,
        "duration_ticks": event.duration_ticks,
        # Where
        "location": event.location,
        "closed_location": event.closed_location,
        # What caused it
        "risk_type": event.risk_type,
        "trigger_factors": list(event.trigger_factors),
        "opened_level": event.opened_level,
        "opened_score": event.opened_score,
        "peak_level": event.peak_level,
        "peak_score": event.peak_score,
        # What the environment looked like
        "environment": environment,
        # What the agent decided
        "decisions": decisions,
        "decision_count": len(decisions),
        "first_response_action": first_protective.get("action") if first_protective else None,
        "response_delay_ticks": (first_protective.get("tick", event.opened_tick) - event.opened_tick) if first_protective else None,
        # What happened afterwards, and whether it worked
        "closed_score": event.closed_score,
        "outcome": event.outcome,
        "outcome_detail": event.outcome_detail,
        "effective": event.outcome in {"avoided", "reduced"},
    }


# ============================================================
# Section 4 -- Agent performance
# ============================================================

def _build_agent_performance(log: SimulationLog) -> dict:
    """Risk avoidance, consistency, response time, route churn, efficiency."""
    decisions = log.decisions
    events = log.risk_events

    resolved = [event for event in events if event.outcome != "active"]
    avoided = sum(1 for event in resolved if event.outcome == "avoided")
    reduced = sum(1 for event in resolved if event.outcome == "reduced")
    worsened = sum(1 for event in resolved if event.outcome == "worsened")
    unresolved = sum(1 for event in events if event.outcome in {"active", "unresolved"})

    # Response time: ticks from a risk opening to the first protective action.
    response_delays = [
        detail for detail in (
            (_first_response_delay(event)) for event in events
        ) if detail is not None
    ]

    # Route churn: a road change that neither reduced risk nor shortened the
    # distance to the ritual target is churn the operator would want to see.
    route_changes = [record for record in decisions if record.action_kind in ROUTE_CHANGE_KINDS]
    successful_changes = [
        record for record in route_changes
        if record.executed and (record.risk_score_after < record.risk_score)
    ]
    unnecessary_changes = [
        record for record in route_changes
        if record.executed and record.risk_level in {"none", "low"} and record.risk_score_after >= record.risk_score
    ]

    # Movement efficiency: of all executed moves, how many shortened the
    # remaining distance to the ritual target on the pilgrim's next decision?
    efficiency = _movement_efficiency(decisions)

    # Consistency: in identical situations (same node + same risk band) did the
    # agent keep choosing the same action, or did it flip-flop?
    consistency, oscillations = _consistency_and_oscillation(decisions)

    return {
        "risk_avoidance": {
            "events_total": len(events),
            "events_resolved": len(resolved),
            "avoided": avoided,
            "reduced": reduced,
            "worsened": worsened,
            "unresolved": unresolved,
            "avoidance_rate_percent": _percent(avoided + reduced, len(resolved)),
        },
        "response_time": {
            "measured_events": len(response_delays),
            "avg_ticks_to_first_response": _round(sum(response_delays) / len(response_delays)) if response_delays else 0.0,
            "immediate_responses": sum(1 for delay in response_delays if delay == 0),
            "slow_responses": sum(1 for delay in response_delays if delay >= 3),
        },
        "route_changes": {
            "total": len(route_changes),
            "successful": len(successful_changes),
            "unnecessary": len(unnecessary_changes),
            "success_rate_percent": _percent(len(successful_changes), len(route_changes)),
        },
        "movement_efficiency": efficiency,
        "decision_consistency": consistency,
        "problematic_behavior": oscillations,
    }


def _first_response_delay(event) -> Optional[int]:
    """Ticks between a risk opening and the agent's first protective action."""
    for decision in event.decisions or []:
        action = str(decision.get("action", ""))
        if action in {"REST", "AVOID_CROWD", "ENTER_PANIC_MODE"} or action.startswith("MOVE_TO_"):
            return max(0, int(decision.get("tick", event.opened_tick)) - event.opened_tick)
    return None


def _movement_efficiency(decisions: List) -> dict:
    """Share of moves that actually shortened the distance to the ritual target."""
    by_pilgrim: Dict[str, List] = defaultdict(list)
    for record in decisions:
        by_pilgrim[record.pilgrim_id].append(record)

    progressing = 0
    regressing = 0
    neutral = 0
    for records in by_pilgrim.values():
        records.sort(key=lambda record: record.tick)
        for current, following in zip(records, records[1:]):
            if not current.moved:
                continue
            if following.distance_hops < current.distance_hops:
                progressing += 1
            elif following.distance_hops > current.distance_hops:
                regressing += 1
            else:
                neutral += 1
    total = progressing + regressing + neutral
    return {
        "measured_moves": total,
        "progressing": progressing,
        "regressing": regressing,
        "neutral": neutral,
        "efficiency_percent": _percent(progressing, total),
    }


def _consistency_and_oscillation(decisions: List) -> tuple:
    """Measure repeat-situation consistency and A->B->A node oscillation."""
    situations: Dict[tuple, Counter] = defaultdict(Counter)
    for record in decisions:
        situations[(record.pilgrim_id, record.location, record.risk_level)][record.action] += 1

    repeated = [counter for counter in situations.values() if sum(counter.values()) > 1]
    consistent = sum(1 for counter in repeated if len(counter) == 1)

    by_pilgrim: Dict[str, List] = defaultdict(list)
    for record in decisions:
        by_pilgrim[record.pilgrim_id].append(record)

    oscillating_pilgrims = []
    for pilgrim_id, records in by_pilgrim.items():
        records.sort(key=lambda record: record.tick)
        nodes = [record.resulting_node or record.location for record in records]
        flips = sum(
            1 for index in range(2, len(nodes))
            if nodes[index] == nodes[index - 2] and nodes[index] != nodes[index - 1]
        )
        if flips >= 2:
            oscillating_pilgrims.append({"pilgrim_id": pilgrim_id, "oscillations": flips})
    oscillating_pilgrims.sort(key=lambda item: item["oscillations"], reverse=True)

    consistency = {
        "repeated_situations": len(repeated),
        "consistent_situations": consistent,
        "consistency_percent": _percent(consistent, len(repeated)),
    }
    problematic = {
        "oscillating_pilgrims": oscillating_pilgrims[:10],
        "total_oscillation_events": sum(item["oscillations"] for item in oscillating_pilgrims),
    }
    return consistency, problematic


# ============================================================
# Section 5 -- Improvements / enhancements
# ============================================================

def _build_improvements(overview: dict, decision_analysis: dict, risk_analysis: dict, performance: dict, llm_status: dict) -> List[dict]:
    """Derive concrete, evidence-backed suggestions from the measured run."""
    suggestions: List[dict] = []

    def suggest(area: str, suggestion: str, evidence: str) -> None:
        suggestions.append({"area": area, "suggestion": suggestion, "evidence": evidence})

    # -- reliability of the LLM path ---------------------------------------
    fallback_share = 100.0 - overview.get("llm_share_percent", 0.0)
    if overview.get("decision_steps", 0) and fallback_share >= 25.0:
        suggest(
            "More reliable fallback logic",
            "A quarter or more of decisions never reached the model. Check the API key, provider and "
            "timeout first; if the failures are budget skips, raise LLM_MAX_CALLS_PER_TICK or narrow "
            "LLM_MAX_AGENTS so the agents you do track are always model-driven.",
            f"{_round(fallback_share)}% of {overview['decision_steps']} decisions used the rule-based fallback.",
        )
    if decision_analysis.get("invalid_or_failed", 0) > 0 and overview.get("llm_share_percent", 0) > 0:
        suggest(
            "Improved prompts",
            "Tighten the response contract: restate the allowed action list immediately before the "
            "JSON schema and set the provider's JSON/structured-output mode, so malformed or "
            "out-of-set actions stop reaching the validator.",
            f"{decision_analysis['invalid_or_failed']} decision(s) fell back after a failed or invalid response.",
        )

    # -- cost / performance -------------------------------------------------
    avg_latency = decision_analysis.get("avg_latency_ms", 0.0)
    if avg_latency >= 1500:
        suggest(
            "Performance improvements",
            "Average model latency is high enough to be felt during playback. Use a smaller/faster model, "
            "shrink the observation (drop remembered_hazards and companions), or decide only on ticks "
            "where the risk band actually changed.",
            f"Average LLM latency was {avg_latency} ms per decision.",
        )
    if llm_status.get("stats", {}).get("cache_hits", 0) == 0 and overview.get("llm_decision_steps", 0) > 50:
        suggest(
            "Reduced unnecessary LLM calls",
            "The situation cache never hit, so near-identical states are each paying for their own call. "
            "Coarsen the cache signature (wider vitals buckets) or cache per zone rather than per node.",
            f"{overview['llm_decision_steps']} model-backed decisions with 0 cache hits.",
        )

    # -- decision quality ---------------------------------------------------
    route_changes = performance.get("route_changes", {})
    if route_changes.get("unnecessary", 0) >= 3:
        suggest(
            "Better decision criteria",
            "Penalise route changes taken at low risk: add an explicit cost line to the prompt "
            "('changing path costs hydration and fatigue and loses ritual progress') so the model only "
            "reroutes when the risk picture justifies it.",
            f"{route_changes['unnecessary']} route change(s) happened at low/no risk without reducing risk.",
        )
    efficiency = performance.get("movement_efficiency", {})
    if efficiency.get("measured_moves", 0) >= 10 and efficiency.get("efficiency_percent", 100.0) < 50.0:
        suggest(
            "Better route selection",
            "Fewer than half of all moves shortened the distance to the ritual target. Include the "
            "next-hop node of the planned route as an explicit field so the model can see which "
            "neighbour is actually forward progress.",
            f"Movement efficiency was {efficiency['efficiency_percent']}% across {efficiency['measured_moves']} moves.",
        )
    problematic = performance.get("problematic_behavior", {})
    if problematic.get("total_oscillation_events", 0) >= 3:
        suggest(
            "Memory of previous situations",
            "Agents bounced between the same two nodes. Feed the last 3 chosen actions (not just visited "
            "nodes) into the prompt and state that reversing the previous move needs a new reason.",
            f"{problematic['total_oscillation_events']} A-to-B-to-A oscillation(s) recorded.",
        )

    # -- risk handling ------------------------------------------------------
    avoidance = performance.get("risk_avoidance", {})
    if avoidance.get("events_resolved", 0) and avoidance.get("avoidance_rate_percent", 100.0) < 60.0:
        suggest(
            "Improved safety behavior",
            "Most risk events were not successfully de-escalated. Make REST and AVOID_CROWD more "
            "attractive in the prompt when hydration is low, and consider auto-escalating to the "
            "rule-based safety ladder above a severe risk score.",
            f"Only {avoidance['avoidance_rate_percent']}% of {avoidance['events_resolved']} resolved risk events "
            "were avoided or reduced.",
        )
    if avoidance.get("unresolved", 0) >= 3:
        suggest(
            "Better risk detection",
            "Several risk events never cleared, which usually means the risk score is driven by a slow "
            "variable (hydration/fatigue) that a single action cannot fix. Split the score into an acute "
            "component and a chronic one so the agent is not permanently alarmed.",
            f"{avoidance['unresolved']} risk event(s) were still open when the run ended.",
        )
    response = performance.get("response_time", {})
    if response.get("slow_responses", 0) >= 2:
        suggest(
            "Better environmental information",
            "Slow first responses suggest the danger was not visible early enough. Add upstream "
            "congestion (occupancy of the *next* node on the route) and a trend field (rising/falling) "
            "to the observation so the model can act before the bottleneck reaches it.",
            f"{response['slow_responses']} risk event(s) waited 3+ ticks for a protective action.",
        )

    worst = risk_analysis.get("worst_event")
    if worst:
        suggest(
            "Better risk detection",
            f"Instrument {worst['location']} specifically -- it produced the run's most severe risk event. "
            "A per-node capacity alarm feeding the observation would let the agent see it forming.",
            f"{worst['event_id']} peaked at risk score {worst['peak_score']} ({worst['risk_type']}) at {worst['location']}.",
        )

    if not suggestions:
        suggestions.append({
            "area": "General",
            "suggestion": "No systemic weakness surfaced in this run. Extend it with a larger agent sample "
                          "(LLM_MAX_AGENTS) and an injected hazard to stress the decision layer harder.",
            "evidence": f"{overview.get('decision_steps', 0)} decisions produced no threshold-crossing problems.",
        })
    return suggestions


# ============================================================
# Section 6 -- Final summary
# ============================================================

def _build_final_summary(overview: dict, decision_analysis: dict, risk_analysis: dict, performance: dict) -> dict:
    """Plain-language wrap-up of the run, grounded in the computed numbers."""
    top_action = decision_analysis["action_counts"][0] if decision_analysis.get("action_counts") else None
    avoidance = performance.get("risk_avoidance", {})
    efficiency = performance.get("movement_efficiency", {})

    what_happened = (
        f"The run covered {overview['ticks_recorded']} tick(s) "
        f"({overview['simulated_hours']} simulated hours) and logged {overview['decision_steps']} "
        f"decision step(s), {overview['llm_decision_steps']} of which were made by the language model "
        f"({overview['llm_share_percent']}%). {overview['movements']} decision(s) resulted in the pilgrim "
        f"actually changing location, and {overview['risk_events_detected']} risk event(s) were detected."
    )

    how_it_behaved = (
        f"Its most frequent choice was {top_action['action']} ({top_action['share_percent']}% of decisions), "
        f"drawing on {decision_analysis['distinct_actions_used']} distinct action(s) overall."
        if top_action else "No decisions were recorded, so no behavioural pattern can be described."
    )

    risk_response = (
        f"Of {avoidance.get('events_resolved', 0)} resolved risk event(s), {avoidance.get('avoided', 0)} were "
        f"avoided outright and {avoidance.get('reduced', 0)} were reduced, with {avoidance.get('worsened', 0)} "
        f"worsening before clearing and {avoidance.get('unresolved', 0)} still open at the end. The agent took "
        f"{performance.get('response_time', {}).get('avg_ticks_to_first_response', 0)} tick(s) on average to "
        "take its first protective action."
        if avoidance.get("events_total") else "No significant risk events occurred, so the agent's emergency behaviour was never tested."
    )

    worked_well: List[str] = []
    needs_work: List[str] = []

    if overview.get("llm_share_percent", 0) >= 75:
        worked_well.append("The LLM path was reliable -- the large majority of decisions reached the model and returned a valid action.")
    else:
        needs_work.append(f"Only {overview.get('llm_share_percent', 0)}% of decisions reached the model; the rest fell back to rules.")

    if avoidance.get("avoidance_rate_percent", 0) >= 60:
        worked_well.append("Risk de-escalation worked: most risk events were avoided or reduced after the agent acted.")
    elif avoidance.get("events_resolved"):
        needs_work.append("Risk de-escalation was weak -- fewer than 60% of resolved events improved.")

    if efficiency.get("efficiency_percent", 0) >= 50:
        worked_well.append("Movement was broadly purposeful: most moves shortened the distance to the ritual target.")
    elif efficiency.get("measured_moves"):
        needs_work.append("Movement was inefficient -- most moves did not shorten the distance to the ritual target.")

    if performance.get("decision_consistency", {}).get("consistency_percent", 0) >= 70:
        worked_well.append("Decisions were consistent: repeat situations usually produced the same action.")
    elif performance.get("decision_consistency", {}).get("repeated_situations"):
        needs_work.append("Decisions were inconsistent across identical situations, which makes behaviour hard to predict.")

    if performance.get("problematic_behavior", {}).get("total_oscillation_events", 0):
        needs_work.append("Some pilgrims oscillated between two nodes instead of committing to a route.")

    return {
        "what_happened": what_happened,
        "how_the_agent_behaved": how_it_behaved,
        "how_it_responded_to_risk": risk_response,
        "what_worked_well": worked_well or ["Nothing stood out as clearly working; the run was too small to judge."],
        "what_needs_improvement": needs_work or ["No systemic weaknesses surfaced in this run."],
        "recommended_technical_enhancements": [
            "Wire the observation's next-hop node and upstream congestion into the prompt for better routing.",
            "Persist the decision log per run so behaviour can be compared across model/prompt versions.",
            "Add a deterministic replay mode (fixed seed + cached model responses) so a prompt change can be A/B tested.",
            "Promote the risk score into an acute/chronic split so slow vitals do not mask sudden danger.",
        ],
    }


# ============================================================
# Public API
# ============================================================

def build_simulation_report(
    log: SimulationLog,
    history: Optional[List[dict]] = None,
    llm_status: Optional[dict] = None,
) -> dict:
    """Build the complete six-section analytical report from the run log."""
    history = history or []
    llm_status = llm_status or {}

    if not log.has_data:
        return {
            "has_data": False,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "message": "No simulation data recorded yet -- advance the simulation at least one tick.",
        }

    overview = _build_overview(log, history)
    decision_analysis = _build_decision_analysis(log)
    risk_analysis = _build_risk_analysis(log)
    performance = _build_agent_performance(log)
    improvements = _build_improvements(overview, decision_analysis, risk_analysis, performance, llm_status)
    final_summary = _build_final_summary(overview, decision_analysis, risk_analysis, performance)

    return {
        "has_data": True,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "llm_configuration": {
            "provider": llm_status.get("provider"),
            "model": llm_status.get("model"),
            "active": llm_status.get("active"),
            "max_agents": llm_status.get("max_agents"),
            "max_calls_per_tick": llm_status.get("max_calls_per_tick"),
            "stats": llm_status.get("stats", {}),
        },
        "overview": overview,
        "decision_analysis": decision_analysis,
        "risk_analysis": risk_analysis,
        "agent_performance": performance,
        "improvements": improvements,
        "final_summary": final_summary,
    }


def render_markdown(report: dict) -> str:
    """Render the report dict as a readable Markdown document."""
    if not report.get("has_data"):
        return f"# HajjSim LLM Simulation Report\n\n{report.get('message', 'No data.')}\n"

    overview = report["overview"]
    decisions = report["decision_analysis"]
    risks = report["risk_analysis"]
    performance = report["agent_performance"]
    summary = report["final_summary"]
    configuration = report.get("llm_configuration", {})

    lines: List[str] = [
        "# HajjSim — LLM Agent Simulation Report",
        "",
        f"_Generated {report['generated_at']}_",
        "",
        f"**Model:** `{configuration.get('provider')}` / `{configuration.get('model')}` — "
        f"active: {configuration.get('active')} · LLM-driven agents: {configuration.get('max_agents')} · "
        f"call budget/tick: {configuration.get('max_calls_per_tick')}",
        "",
        "## 1. Simulation Overview",
        "",
        f"- **Duration:** {overview['ticks_recorded']} ticks × {overview['minutes_per_tick']} min "
        f"= {overview['simulated_hours']} simulated hours ({overview['simulated_days']} days); "
        f"{overview['wall_clock_seconds']}s wall clock",
        f"- **Decision steps:** {overview['decision_steps']} "
        f"({overview['llm_decision_steps']} from the LLM = {overview['llm_share_percent']}%, "
        f"{overview['fallback_decision_steps']} from the rule-based fallback)",
        f"- **Movements:** {overview['movements']} ({overview['movement_share_percent']}% of decisions)",
        f"- **Risks detected:** {overview['risk_events_detected']} risk events, "
        f"{overview['risk_detections_per_tick']} agents in a risk band per tick on average",
        f"- **Agents at end:** {overview['agents_at_end']} · run reached completion: {overview['run_completed']}",
        "",
        "## 2. Decision Analysis",
        "",
        "| Action | Count | Share |",
        "| --- | ---: | ---: |",
    ]
    for entry in decisions["action_counts"][:12]:
        lines.append(f"| `{entry['action']}` | {entry['count']} | {entry['share_percent']}% |")

    lines += [
        "",
        f"Decision sources: " + ", ".join(
            f"`{entry['source']}` {entry['count']} ({entry['share_percent']}%)" for entry in decisions["source_counts"]
        ) or "none",
        f"Average model latency: {decisions['avg_latency_ms']} ms · "
        f"fallbacks after failure/invalid output: {decisions['invalid_or_failed']}",
        "",
        "### Important decision points",
        "",
    ]
    if decisions["key_decision_points"]:
        for point in decisions["key_decision_points"]:
            lines.append(
                f"- **Tick {point['tick']}** · `{point['pilgrim_id']}` at **{point['location']}** "
                f"(risk {point['risk_level']} {point['risk_score']}, {point['options_offered']} options) → "
                f"**{point['action']}** — _{point['reason'] or 'no reason given'}_ "
                f"(risk after: {point['risk_score_after']})"
            )
    else:
        lines.append("- None: no decision was taken while the agent was in a high or severe risk band.")

    lines += ["", "### Successful decisions", ""]
    if decisions["successful_examples"]:
        for example in decisions["successful_examples"]:
            lines.append(
                f"- Tick {example['tick']} · `{example['pilgrim_id']}` chose **{example['action']}** at "
                f"{example['location']} → risk {example['risk_score']} → {example['risk_score_after']} "
                f"({example['risk_delta']}). _{example['reason']}_"
            )
    else:
        lines.append("- None recorded.")

    lines += ["", "### Unsuccessful decisions", ""]
    if decisions["unsuccessful_examples"]:
        for example in decisions["unsuccessful_examples"]:
            lines.append(
                f"- Tick {example['tick']} · `{example['pilgrim_id']}` chose **{example['action']}** at "
                f"{example['location']} → risk {example['risk_score']} → {example['risk_score_after']} "
                f"(+{example['risk_delta']}). _{example['reason']}_"
            )
    else:
        lines.append("- None recorded.")

    lines += [
        "",
        "## 3. Risk Analysis",
        "",
        f"{risks['total_events']} risk event(s) recorded, averaging "
        f"{risks.get('avg_duration_ticks', 0)} tick(s) each.",
        "",
    ]
    if risks["risk_type_counts"]:
        lines.append("Risk types: " + ", ".join(
            f"`{entry['risk_type']}` ×{entry['count']}" for entry in risks["risk_type_counts"]
        ))
        lines.append("")
        lines.append("Outcomes: " + ", ".join(
            f"**{entry['outcome']}** {entry['count']} ({entry['share_percent']}%)" for entry in risks["outcome_counts"]
        ))
        lines.append("")

    for event in risks["significant_events"]:
        lines += [
            f"### {event['event_id']} — {event['risk_type']} · `{event['pilgrim_id']}`",
            "",
            f"- **When:** tick {event['opened_tick']} ({event['opened_time']}), lasting {event['duration_ticks']} tick(s)",
            f"- **Where:** {event['location']}" + (f" → {event['closed_location']}" if event['closed_location'] else ""),
            f"- **Trigger:** {', '.join(event['trigger_factors']) or 'unspecified'}",
            f"- **Environment:** density {event['environment'].get('crowd_density')}, "
            f"{event['environment'].get('temperature_c')} °C, hazard: {event['environment'].get('hazard') or 'none'}, "
            f"node {event['environment'].get('occupancy')}/{event['environment'].get('capacity')}",
            f"- **Severity:** opened at {event['opened_score']} ({event['opened_level']}), peaked at {event['peak_score']} ({event['peak_level']})",
            f"- **Decisions taken:** {event['decision_count']}"
            + (f", first response `{event['first_response_action']}` after {event['response_delay_ticks']} tick(s)"
               if event['first_response_action'] else ", no protective action recorded"),
        ]
        for decision in event["decisions"][:5]:
            lines.append(
                f"    - tick {decision['tick']}: `{decision['action']}` ({decision['source']}) — "
                f"_{decision.get('reason') or 'no reason given'}_"
            )
        lines += [
            f"- **Aftermath:** {event['outcome_detail']}",
            f"- **Effective?** {'Yes' if event['effective'] else 'No'} (outcome: {event['outcome']})",
            "",
        ]
    if not risks["significant_events"]:
        lines += ["No significant risk events were recorded in this run.", ""]

    avoidance = performance["risk_avoidance"]
    response = performance["response_time"]
    route = performance["route_changes"]
    efficiency = performance["movement_efficiency"]
    consistency = performance["decision_consistency"]
    problematic = performance["problematic_behavior"]

    lines += [
        "## 4. Agent Performance",
        "",
        f"- **Risk avoidance:** {avoidance['avoided']} avoided · {avoidance['reduced']} reduced · "
        f"{avoidance['worsened']} worsened · {avoidance['unresolved']} unresolved "
        f"→ **{avoidance['avoidance_rate_percent']}%** of resolved events improved",
        f"- **Response time:** {response['avg_ticks_to_first_response']} tick(s) on average to the first "
        f"protective action ({response['immediate_responses']} immediate, {response['slow_responses']} slow)",
        f"- **Route changes:** {route['total']} total · {route['successful']} successful "
        f"({route['success_rate_percent']}%) · {route['unnecessary']} unnecessary",
        f"- **Movement efficiency:** {efficiency['efficiency_percent']}% of "
        f"{efficiency['measured_moves']} measured moves shortened the distance to the ritual target "
        f"({efficiency['regressing']} moved away from it)",
        f"- **Decision consistency:** {consistency['consistency_percent']}% of "
        f"{consistency['repeated_situations']} repeated situations produced the same action",
        f"- **Repeated/problematic behaviour:** {problematic['total_oscillation_events']} oscillation event(s)"
        + (f" across {len(problematic['oscillating_pilgrims'])} pilgrim(s)" if problematic['oscillating_pilgrims'] else ""),
        "",
        "## 5. Improvements / Enhancements",
        "",
    ]
    for item in report["improvements"]:
        lines.append(f"- **{item['area']}** — {item['suggestion']}")
        lines.append(f"  - _Evidence:_ {item['evidence']}")

    lines += [
        "",
        "## 6. Final Summary",
        "",
        f"**What happened.** {summary['what_happened']}",
        "",
        f"**How the agent behaved.** {summary['how_the_agent_behaved']}",
        "",
        f"**How it responded to risk.** {summary['how_it_responded_to_risk']}",
        "",
        "**What worked well.**",
        "",
    ]
    lines += [f"- {item}" for item in summary["what_worked_well"]]
    lines += ["", "**What needs improvement.**", ""]
    lines += [f"- {item}" for item in summary["what_needs_improvement"]]
    lines += ["", "**Recommended technical enhancements.**", ""]
    lines += [f"- {item}" for item in summary["recommended_technical_enhancements"]]
    lines.append("")
    return "\n".join(lines)


def write_report(report: dict, directory: Path, basename: Optional[str] = None) -> Dict[str, str]:
    """Write the report to ``reports/`` as both Markdown and JSON."""
    directory.mkdir(parents=True, exist_ok=True)
    stamp = basename or datetime.now().strftime("run_%Y%m%d_%H%M%S")
    markdown_path = directory / f"{stamp}.md"
    json_path = directory / f"{stamp}.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return {"markdown": str(markdown_path), "json": str(json_path)}
