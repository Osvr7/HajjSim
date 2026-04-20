import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple


# ==========================================
# LAYER 1: STATIC PROFILE (WHO THE PILGRIM IS)
# ==========================================
@dataclass(frozen=True)
class StaticProfile:
    pilgrim_id: str
    age: int
    nationality: str
    group_id: str
    mobility: float
    health_status: str = "stable"
    chronic_conditions: Tuple[str, ...] = field(default_factory=tuple)
    language: str = "Arabic"
    risk_tolerance: float = 0.5


# ==========================================
# LAYER 2: DYNAMIC STATE (WHAT IS CHANGING NOW)
# ==========================================
@dataclass
class DynamicState:
    current_node: str
    target_node: str = "Arafat"
    position_xy: Optional[Tuple[float, float]] = None
    fatigue: float = 0.0
    stress: float = 0.0
    hydration: float = 100.0
    is_panicking: bool = False
    is_with_group: bool = True
    last_action: str = "idle"
    simulation_tick: int = 0


# ==========================================
# LAYER 3: MEMORY (WHAT THE PILGRIM REMEMBERS)
# ==========================================
@dataclass
class ShortTermMemory:
    recent_nodes: List[str] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)
    max_recent_nodes: int = 5
    max_recent_events: int = 10

    def remember_node(self, node: str) -> None:
        self.recent_nodes.append(node)
        if len(self.recent_nodes) > self.max_recent_nodes:
            self.recent_nodes.pop(0)

    def remember_event(self, event: str) -> None:
        self.recent_events.append(event)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop(0)


@dataclass
class LongTermMemory:
    known_routes: Dict[str, List[str]] = field(default_factory=dict)
    known_hazards: Dict[str, str] = field(default_factory=dict)
    learned_preferences: Dict[str, float] = field(default_factory=dict)
    ritual_progress: List[str] = field(default_factory=list)


@dataclass
class SocialMemory:
    leader_id: Optional[str] = None
    known_companions: List[str] = field(default_factory=list)
    group_last_seen_node: Optional[str] = None
    help_contacts: List[str] = field(default_factory=list)


@dataclass
class Memory:
    short_term: ShortTermMemory = field(default_factory=ShortTermMemory)
    long_term: LongTermMemory = field(default_factory=LongTermMemory)
    social: SocialMemory = field(default_factory=SocialMemory)


# ==========================================
# LAYER 4: BEHAVIOR ENGINE (HOW THE PILGRIM DECIDES)
# ==========================================
class BehaviorEngine:
    def __init__(
        self,
        agent_reference: "PilgrimAgent",
        llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
    ):
        self.agent = agent_reference
        self.llm_override = llm_override

    def decide_action(self, environment_data: dict) -> str:
        rule_based_action = self._rule_based_decision(environment_data)
        llm_action = self._apply_llm_override(environment_data, rule_based_action)
        return llm_action or rule_based_action

    def _rule_based_decision(self, environment_data: dict) -> str:
        state = self.agent.state
        profile = self.agent.profile
        social = self.agent.memory.social

        if state.stress >= 85.0:
            return "ENTER_PANIC_MODE"

        if state.fatigue >= 75.0 or state.hydration <= 30.0:
            return "REST"

        if not state.is_with_group and social.group_last_seen_node:
            return f"MOVE_TO_{social.group_last_seen_node}"

        density = environment_data.get("density", 0.0)
        if density >= 6.0 and profile.risk_tolerance < 0.7:
            return "AVOID_CROWD"

        return f"MOVE_TO_{state.target_node}"

    def _apply_llm_override(self, environment_data: dict, proposed_action: str) -> Optional[str]:
        if not self.llm_override:
            return None
        return self.llm_override(self.agent, environment_data, proposed_action)


# ==========================================
# MASTER AGENT
# ==========================================
class PilgrimAgent:
    def __init__(
        self,
        static_profile: StaticProfile,
        initial_node: str,
        target_node: str = "Arafat",
        llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
    ):
        self.profile = static_profile
        self.state = DynamicState(current_node=initial_node, target_node=target_node)
        self.memory = Memory()
        self.brain = BehaviorEngine(self, llm_override=llm_override)

    def step(self, environment_data: dict) -> str:
        self.state.simulation_tick += 1
        self._perceive_environment(environment_data)
        action = self.brain.decide_action(environment_data)
        self._execute_action(action, environment_data)
        return action

    def _perceive_environment(self, environment_data: dict) -> None:
        density = float(environment_data.get("density", 0.0))
        temperature = float(environment_data.get("temperature", 32.0))
        hazard = environment_data.get("hazard")
        visible_group_node = environment_data.get("group_location")

        stress_gain = max(0.0, density - 3.0) * 4.0
        fatigue_gain = max(0.5, 1.5 - self.profile.mobility)
        hydration_loss = max(1.0, (temperature - 28.0) * 0.4)

        if self.profile.health_status.lower() != "stable":
            fatigue_gain += 0.5
            stress_gain += 2.0

        self.state.stress = min(100.0, self.state.stress + stress_gain)
        self.state.fatigue = min(100.0, self.state.fatigue + fatigue_gain)
        self.state.hydration = max(0.0, self.state.hydration - hydration_loss)
        self.state.is_panicking = self.state.stress >= 85.0

        if hazard:
            self.memory.long_term.known_hazards[self.state.current_node] = str(hazard)
            self.memory.short_term.remember_event(f"Hazard seen: {hazard}")

        if visible_group_node:
            self.memory.social.group_last_seen_node = visible_group_node
            self.state.is_with_group = visible_group_node == self.state.current_node

    def _execute_action(self, action: str, environment_data: dict) -> None:
        self.memory.short_term.remember_node(self.state.current_node)
        self.memory.short_term.remember_event(f"Tick {self.state.simulation_tick}: {action}")
        self.state.last_action = action

        if action == "REST":
            self.state.fatigue = max(0.0, self.state.fatigue - 8.0)
            self.state.stress = max(0.0, self.state.stress - 5.0)
            self.state.hydration = min(100.0, self.state.hydration + 10.0)
            return

        if action == "AVOID_CROWD":
            alternate_node = environment_data.get("alternate_node", self.state.current_node)
            self.state.current_node = alternate_node
            self.state.stress = max(0.0, self.state.stress - 3.0)
            return

        if action == "ENTER_PANIC_MODE":
            self.state.is_panicking = True
            panic_node = environment_data.get("panic_node", self.state.current_node)
            self.state.current_node = panic_node
            return

        if action.startswith("MOVE_TO_"):
            destination = action.replace("MOVE_TO_", "", 1)
            self.state.current_node = destination
            self.memory.long_term.known_routes.setdefault(
                self.state.target_node,
                [],
            ).append(destination)

    def get_snapshot(self) -> dict:
        return {
            "profile": {
                "pilgrim_id": self.profile.pilgrim_id,
                "age": self.profile.age,
                "nationality": self.profile.nationality,
                "group_id": self.profile.group_id,
                "mobility": self.profile.mobility,
                "health_status": self.profile.health_status,
                "chronic_conditions": list(self.profile.chronic_conditions),
                "language": self.profile.language,
                "risk_tolerance": self.profile.risk_tolerance,
            },
            "state": {
                "current_node": self.state.current_node,
                "target_node": self.state.target_node,
                "fatigue": self.state.fatigue,
                "stress": self.state.stress,
                "hydration": self.state.hydration,
                "is_panicking": self.state.is_panicking,
                "is_with_group": self.state.is_with_group,
                "last_action": self.state.last_action,
                "simulation_tick": self.state.simulation_tick,
            },
            "memory": {
                "short_term": {
                    "recent_nodes": self.memory.short_term.recent_nodes,
                    "recent_events": self.memory.short_term.recent_events,
                },
                "long_term": {
                    "known_routes": self.memory.long_term.known_routes,
                    "known_hazards": self.memory.long_term.known_hazards,
                    "learned_preferences": self.memory.long_term.learned_preferences,
                    "ritual_progress": self.memory.long_term.ritual_progress,
                },
                "social": {
                    "leader_id": self.memory.social.leader_id,
                    "known_companions": self.memory.social.known_companions,
                    "group_last_seen_node": self.memory.social.group_last_seen_node,
                    "help_contacts": self.memory.social.help_contacts,
                },
            },
        }


class AgentFactory:
    """Creates large numbers of pilgrim variants from configurable distributions."""

    DEFAULT_NATIONALITIES: Sequence[Tuple[str, str]] = (
        ("Saudi", "Arabic"),
        ("Indonesian", "Bahasa Indonesia"),
        ("Nigerian", "English"),
        ("Pakistani", "Urdu"),
        ("Turkish", "Turkish"),
    )
    DEFAULT_INITIAL_NODES: Sequence[str] = (
        "Mina_Camp_1",
        "Mina_Camp_2",
        "Mina_Camp_4",
        "Jamarat_Bridge",
        "Arafat_Gate",
    )
    DEFAULT_TARGET_NODES: Sequence[str] = (
        "Arafat",
        "Muzdalifah",
        "Jamarat",
    )
    DEFAULT_HEALTH_WEIGHTS: Dict[str, float] = {
        "stable": 0.7,
        "needs_support": 0.2,
        "high_risk": 0.1,
    }
    DEFAULT_CONDITIONS_BY_HEALTH: Dict[str, Sequence[str]] = {
        "stable": (),
        "needs_support": ("diabetes", "hypertension", "arthritis"),
        "high_risk": ("heart_disease", "respiratory_issue", "mobility_impairment"),
    }

    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)

    def create_agent(
        self,
        pilgrim_id: str,
        age: int,
        nationality: str,
        group_id: str,
        mobility: float,
        health_status: str,
        initial_node: str,
        target_node: str,
        language: str,
        chronic_conditions: Optional[Sequence[str]] = None,
        risk_tolerance: Optional[float] = None,
        llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
    ) -> PilgrimAgent:
        profile = StaticProfile(
            pilgrim_id=pilgrim_id,
            age=age,
            nationality=nationality,
            group_id=group_id,
            mobility=mobility,
            health_status=health_status,
            chronic_conditions=tuple(chronic_conditions or ()),
            language=language,
            risk_tolerance=risk_tolerance if risk_tolerance is not None else self._derive_risk_tolerance(age, health_status),
        )
        return PilgrimAgent(
            static_profile=profile,
            initial_node=initial_node,
            target_node=target_node,
            llm_override=llm_override,
        )

    def generate_agent(
        self,
        index: int,
        group_id: Optional[str] = None,
        target_node: Optional[str] = None,
        llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
    ) -> PilgrimAgent:
        nationality, language = self.random.choice(list(self.DEFAULT_NATIONALITIES))
        age = self.random.randint(18, 85)
        health_status = self._weighted_choice(self.DEFAULT_HEALTH_WEIGHTS)
        mobility = self._derive_mobility(age, health_status)
        chronic_conditions = self._sample_conditions(health_status)
        pilgrim_group = group_id or f"G_{100 + ((index - 1) // 10):03d}"

        agent = self.create_agent(
            pilgrim_id=f"P_{index:04d}",
            age=age,
            nationality=nationality,
            group_id=pilgrim_group,
            mobility=mobility,
            health_status=health_status,
            initial_node=self.random.choice(list(self.DEFAULT_INITIAL_NODES)),
            target_node=target_node or self.random.choice(list(self.DEFAULT_TARGET_NODES)),
            language=language,
            chronic_conditions=chronic_conditions,
            llm_override=llm_override,
        )
        self._seed_memory(agent)
        return agent

    def generate_agents(
        self,
        count: int,
        start_index: int = 1,
        llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
    ) -> Dict[str, PilgrimAgent]:
        agents = {}
        for index in range(start_index, start_index + count):
            agent = self.generate_agent(index=index, llm_override=llm_override)
            agents[agent.profile.pilgrim_id] = agent
        self._link_social_groups(agents)
        return agents

    def agent_to_record(self, agent: PilgrimAgent) -> dict:
        snapshot = agent.get_snapshot()
        return {
            "pilgrim_id": snapshot["profile"]["pilgrim_id"],
            "age": snapshot["profile"]["age"],
            "nationality": snapshot["profile"]["nationality"],
            "group_id": snapshot["profile"]["group_id"],
            "mobility": snapshot["profile"]["mobility"],
            "health_status": snapshot["profile"]["health_status"],
            "chronic_conditions": snapshot["profile"]["chronic_conditions"],
            "language": snapshot["profile"]["language"],
            "risk_tolerance": snapshot["profile"]["risk_tolerance"],
            "initial_node": snapshot["state"]["current_node"],
            "target_node": snapshot["state"]["target_node"],
            "social_memory": snapshot["memory"]["social"],
            "long_term_memory": snapshot["memory"]["long_term"],
        }

    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        options = list(weights.keys())
        values = list(weights.values())
        return self.random.choices(options, weights=values, k=1)[0]

    def _derive_mobility(self, age: int, health_status: str) -> float:
        mobility = 1.15 - max(age - 20, 0) * 0.008
        if health_status == "needs_support":
            mobility -= 0.15
        elif health_status == "high_risk":
            mobility -= 0.30
        return round(min(1.2, max(0.35, mobility)), 2)

    def _derive_risk_tolerance(self, age: int, health_status: str) -> float:
        risk = 0.75 - max(age - 20, 0) * 0.004
        if health_status == "needs_support":
            risk -= 0.1
        elif health_status == "high_risk":
            risk -= 0.2
        jitter = self.random.uniform(-0.08, 0.08)
        return round(min(0.95, max(0.1, risk + jitter)), 2)

    def _sample_conditions(self, health_status: str) -> Tuple[str, ...]:
        available = list(self.DEFAULT_CONDITIONS_BY_HEALTH.get(health_status, ()))
        if not available:
            return ()
        condition_count = 1 if health_status == "needs_support" else min(2, len(available))
        return tuple(self.random.sample(available, k=condition_count))

    def _seed_memory(self, agent: PilgrimAgent) -> None:
        preferred_route = [agent.state.current_node, "Transit_Corridor", agent.state.target_node]
        agent.memory.long_term.known_routes[agent.state.target_node] = preferred_route
        agent.memory.long_term.learned_preferences = {
            "avoid_dense_areas": round(1.0 - agent.profile.risk_tolerance, 2),
            "prefer_shaded_route": round(self.random.uniform(0.3, 0.95), 2),
        }
        agent.memory.long_term.ritual_progress = ["arrival_registered"]
        if agent.profile.health_status != "stable":
            agent.memory.social.help_contacts = ["Medical_Desk_1"]

    def _link_social_groups(self, agents: Dict[str, PilgrimAgent]) -> None:
        grouped: Dict[str, List[PilgrimAgent]] = {}
        for agent in agents.values():
            grouped.setdefault(agent.profile.group_id, []).append(agent)

        for group_members in grouped.values():
            member_ids = [member.profile.pilgrim_id for member in group_members]
            leader_id = member_ids[0]
            leader_node = group_members[0].state.current_node
            for member in group_members:
                member.memory.social.leader_id = leader_id if member.profile.pilgrim_id != leader_id else None
                member.memory.social.known_companions = [
                    member_id for member_id in member_ids if member_id != member.profile.pilgrim_id
                ]
                member.memory.social.group_last_seen_node = leader_node


def build_agent_from_record(
    item: dict,
    llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
) -> PilgrimAgent:
    profile = StaticProfile(
        pilgrim_id=item["pilgrim_id"],
        age=int(item["age"]),
        nationality=item["nationality"],
        group_id=item["group_id"],
        mobility=float(item.get("mobility", item.get("base_mobility", 1.0))),
        health_status=item.get("health_status", "stable"),
        chronic_conditions=tuple(item.get("chronic_conditions", [])),
        language=item.get("language", "Arabic"),
        risk_tolerance=float(item.get("risk_tolerance", 0.5)),
    )

    agent = PilgrimAgent(
        static_profile=profile,
        initial_node=item["initial_node"],
        target_node=item.get("target_node", "Arafat"),
        llm_override=llm_override,
    )

    social_memory = item.get("social_memory", {})
    agent.memory.social.leader_id = social_memory.get("leader_id")
    agent.memory.social.known_companions = social_memory.get("known_companions", [])
    agent.memory.social.help_contacts = social_memory.get("help_contacts", [])
    agent.memory.social.group_last_seen_node = social_memory.get("group_last_seen_node")

    long_term_memory = item.get("long_term_memory", {})
    agent.memory.long_term.known_routes = long_term_memory.get("known_routes", {})
    agent.memory.long_term.known_hazards = long_term_memory.get("known_hazards", {})
    agent.memory.long_term.learned_preferences = long_term_memory.get(
        "learned_preferences",
        {},
    )
    agent.memory.long_term.ritual_progress = long_term_memory.get("ritual_progress", [])

    return agent


def build_manual_agent(
    pilgrim_id: str,
    age: int,
    nationality: str,
    group_id: str,
    mobility: float,
    health_status: str,
    initial_node: str,
    target_node: str,
    language: str = "Arabic",
    chronic_conditions: Optional[Sequence[str]] = None,
    risk_tolerance: float = 0.5,
    llm_override: Optional[Callable[["PilgrimAgent", dict, str], Optional[str]]] = None,
) -> PilgrimAgent:
    factory = AgentFactory()
    agent = factory.create_agent(
        pilgrim_id=pilgrim_id,
        age=int(age),
        nationality=nationality,
        group_id=group_id,
        mobility=float(mobility),
        health_status=health_status,
        initial_node=initial_node,
        target_node=target_node,
        language=language,
        chronic_conditions=tuple(chronic_conditions or ()),
        risk_tolerance=float(risk_tolerance),
        llm_override=llm_override,
    )
    factory._seed_memory(agent)
    return agent
