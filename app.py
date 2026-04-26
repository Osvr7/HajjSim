import json
from collections import Counter
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


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web"
DATA_FILE = BASE_DIR / "pilgrims.json"


@dataclass
class EnvironmentState:
    density: float = 5.0
    temperature: float = 37.0
    hazard: str = "none"
    group_location: str = "Makkah_Airport"
    alternate_node: str = "Shade_Corridor"
    panic_node: str = "Emergency_Point"
    tick: int = -1

    def _current_tick_state(self):
        return get_simulation_tick_payload(self.tick)

    def apply_updates(self, payload: dict) -> None:
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

    def to_payload(self) -> dict:
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
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.factory = AgentFactory(seed=42)
        self.agents = {}
        self._next_index = 1
        self.load()

    def load(self) -> None:
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
        return [agent.get_snapshot() for agent in self.agents.values()]

    def create_manual_agent(self, payload: dict) -> dict:
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
        )
        self.agents[agent.profile.pilgrim_id] = agent
        self._advance_index(agent.profile.pilgrim_id)
        return agent.get_snapshot()

    def generate_random_agents(self, count: int) -> list[dict]:
        generated = self.factory.generate_agents(count=count, start_index=self._next_index)
        self.agents.update(generated)
        self._next_index += count
        return [agent.get_snapshot() for agent in generated.values()]

    def step_all(self, environment_data: dict) -> list[dict]:
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

    def sync_all(self, environment_data: dict) -> None:
        for agent in self.agents.values():
            agent.sync_with_environment(environment_data)

    def reset_ritual_days(self) -> None:
        for agent in self.agents.values():
            agent.reset_ritual_cycle()

    def _advance_index(self, pilgrim_id: str) -> None:
        digits = "".join(char for char in pilgrim_id if char.isdigit())
        if digits:
            self._next_index = max(self._next_index, int(digits) + 1)
        else:
            self._next_index += 1

    def _parse_conditions(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []


REPOSITORY = AgentRepository(DATA_FILE)
ENVIRONMENT = EnvironmentState()


class HajjSimHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/agents":
            self._send_json({"agents": REPOSITORY.list_agents()})
            return
        if parsed.path == "/api/summary":
            self._send_json(self._build_summary())
            return
        if parsed.path == "/api/environment":
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return
        if parsed.path in ("/", "/index.html"):
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else ""
        payload = self._parse_body(raw_body)

        if parsed.path == "/api/agents":
            snapshot = REPOSITORY.create_manual_agent(payload)
            self._send_json({"agent": snapshot}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/agents/random":
            count = max(1, min(500, int(payload.get("count", 10))))
            agents = REPOSITORY.generate_random_agents(count)
            self._send_json({"agents": agents}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/environment":
            ENVIRONMENT.apply_updates(payload)
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return

        if parsed.path == "/api/simulate/step":
            ENVIRONMENT.apply_updates(payload)
            actions = REPOSITORY.step_all(ENVIRONMENT.to_payload())
            ENVIRONMENT.tick += 1
            self._send_json(
                {
                    "environment": ENVIRONMENT.to_dict(),
                    "actions": actions,
                    "summary": self._build_summary(),
                }
            )
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def _parse_body(self, raw_body: str) -> dict:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(raw_body or "{}")
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(raw_body)
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
        return {}

    def _build_summary(self) -> dict:
        agents = REPOSITORY.list_agents()
        total = len(agents)
        stable = 0
        needs_support = 0
        high_risk = 0
        panicking = 0

    for agent in agents:
        risk_level = derive_operational_status(agent)
        if risk_level == "panicking":
            panicking += 1
        elif risk_level == "high_risk":
            high_risk += 1
        elif risk_level == "needs_support":
            needs_support += 1
        else:
            stable += 1

        avg_stress = round(
            sum(agent["state"]["stress"] for agent in agents) / total,
            1,
        ) if total else 0.0
        avg_fatigue = round(
            sum(agent["state"]["fatigue"] for agent in agents) / total,
            1,
        ) if total else 0.0
        avg_hydration = round(
            sum(agent["state"]["hydration"] for agent in agents) / total,
            1,
        ) if total else 0.0
        severity_index = round(
            ((panicking * 1.0) + (high_risk * 0.7) + (needs_support * 0.4)) / total * 100,
            1,
        ) if total else 0.0

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
            "simulation_tick": ENVIRONMENT.tick,
        }


def update_summary_history() -> dict:
    summary = build_summary_snapshot()
    entry = {**summary}
    if SUMMARY_HISTORY and SUMMARY_HISTORY[-1]["simulation_tick"] == entry["simulation_tick"]:
        SUMMARY_HISTORY[-1] = entry
    else:
        SUMMARY_HISTORY.append(entry)
    return summary


update_summary_history()


class HajjSimHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/agents":
            self._send_json({"agents": REPOSITORY.list_agents()})
            return
        if parsed.path == "/api/summary":
            self._send_json({
                "summary": build_summary_snapshot(),
                "history": SUMMARY_HISTORY,
            })
            return
        if parsed.path == "/api/environment":
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return
        if parsed.path in ("/", "/index.html"):
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else ""
        payload = self._parse_body(raw_body)

        if parsed.path == "/api/agents":
            snapshot = REPOSITORY.create_manual_agent(payload)
            update_summary_history()
            self._send_json({"agent": snapshot}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/agents/random":
            count = max(1, min(500, int(payload.get("count", 10))))
            agents = REPOSITORY.generate_random_agents(count)
            update_summary_history()
            self._send_json({"agents": agents}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/environment":
            ENVIRONMENT.apply_updates(payload)
            self._send_json({"environment": ENVIRONMENT.to_dict()})
            return

        if parsed.path == "/api/simulate/step":
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

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def _parse_body(self, raw_body: str) -> dict:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(raw_body or "{}")
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(raw_body)
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
        return {}

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), HajjSimHandler)
    print(f"HajjSim web app running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
