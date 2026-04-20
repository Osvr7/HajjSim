import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from hajj_agents import AgentFactory, build_agent_from_record, build_manual_agent


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web"
DATA_FILE = BASE_DIR / "pilgrims.json"


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
            chronic_conditions=self._split_csv(payload.get("chronic_conditions", "")),
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

    def _advance_index(self, pilgrim_id: str) -> None:
        digits = "".join(char for char in pilgrim_id if char.isdigit())
        if digits:
            self._next_index = max(self._next_index, int(digits) + 1)
        else:
            self._next_index += 1

    def _split_csv(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]


REPOSITORY = AgentRepository(DATA_FILE)


class HajjSimHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/agents":
            self._send_json({"agents": REPOSITORY.list_agents()})
            return
        if parsed.path == "/api/summary":
            self._send_json(self._build_summary())
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

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def _parse_body(self, raw_body: str) -> dict:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(raw_body or "{}")
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(raw_body)
            return {key: values[0] for key, values in parsed.items()}
        return {}

    def _build_summary(self) -> dict:
        agents = REPOSITORY.list_agents()
        total = len(agents)
        panicking = sum(1 for agent in agents if agent["state"]["is_panicking"])
        avg_stress = round(
            sum(agent["state"]["stress"] for agent in agents) / total,
            1,
        ) if total else 0.0
        avg_fatigue = round(
            sum(agent["state"]["fatigue"] for agent in agents) / total,
            1,
        ) if total else 0.0
        return {
            "total_agents": total,
            "panicking_agents": panicking,
            "avg_stress": avg_stress,
            "avg_fatigue": avg_fatigue,
        }

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
