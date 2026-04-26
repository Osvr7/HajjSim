import random
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class RitualStep:
    sequence_order: int
    scheduled_day_index: int
    scheduled_day_label: str
    ritual_name: str
    target_node: str
    progress_key: str
    description: str


@dataclass(frozen=True)
class SimulationDaySlot:
    day_index: int
    label: str
    rituals: Tuple[str, ...]


HAJJ_DAY_SLOTS: Tuple[SimulationDaySlot, ...] = (
    SimulationDaySlot(
        day_index=0,
        label="Upon Arrival in Makkah",
        rituals=("Tawaf Al-Qudoum (Arrival Tawaf)",),
    ),
    SimulationDaySlot(
        day_index=1,
        label="8th of Dhul-Hijjah",
        rituals=("Stay in Mina",),
    ),
    SimulationDaySlot(
        day_index=2,
        label="9th of Dhul-Hijjah",
        rituals=("Wuquf at Arafah",),
    ),
    SimulationDaySlot(
        day_index=3,
        label="Night of 9th to 10th Dhul-Hijjah",
        rituals=("Stay in Muzdalifah",),
    ),
    SimulationDaySlot(
        day_index=4,
        label="10th of Dhul-Hijjah",
        rituals=(
            "Ramy at Aqaba",
            "Sacrifice",
            "Tawaf al-Ifadhah and Sa'y",
        ),
    ),
    SimulationDaySlot(
        day_index=5,
        label="Night of 10th Dhul-Hijjah",
        rituals=("Night in Mina",),
    ),
    SimulationDaySlot(
        day_index=6,
        label="11th of Dhul-Hijjah",
        rituals=("Mina Stay",),
    ),
    SimulationDaySlot(
        day_index=7,
        label="12th of Dhul-Hijjah",
        rituals=("Mina Stay",),
    ),
    SimulationDaySlot(
        day_index=8,
        label="13th of Dhul-Hijjah",
        rituals=("Mina Stay",),
    ),
    SimulationDaySlot(
        day_index=9,
        label="After completing Hajj, usually 12th or 13th",
        rituals=("Tawaf al-Wadaa",),
    ),
)


HAJJ_RITUAL_SCHEDULE: Tuple[RitualStep, ...] = (
    RitualStep(
        sequence_order=1,
        scheduled_day_index=0,
        scheduled_day_label="Upon Arrival in Makkah",
        ritual_name="Tawaf Al-Qudoum (Arrival Tawaf)",
        target_node="Tawaf_Area",
        progress_key="tawaf_qudoum_complete",
        description="Pilgrims begin the Hajj rites with Tawaf Al-Qudoum after arriving for Hajj.",
    ),
    RitualStep(
        sequence_order=2,
        scheduled_day_index=1,
        scheduled_day_label="8th of Dhul-Hijjah",
        ritual_name="Stay in Mina",
        target_node="Mina_Camps_Core",
        progress_key="mina_tarwiyah_complete",
        description="Pilgrims move to Mina and spend the Day of Tarwiyah there.",
    ),
    RitualStep(
        sequence_order=3,
        scheduled_day_index=2,
        scheduled_day_label="9th of Dhul-Hijjah",
        ritual_name="Wuquf at Arafah",
        target_node="Arafat_Main_Field",
        progress_key="arafah_complete",
        description="Pilgrims stand at Arafah for prayer, reflection, and supplication.",
    ),
    RitualStep(
        sequence_order=4,
        scheduled_day_index=3,
        scheduled_day_label="Night of 9th to 10th Dhul-Hijjah",
        ritual_name="Stay in Muzdalifah",
        target_node="Muzdalifah_Open_Area",
        progress_key="muzdalifah_complete",
        description="Pilgrims stay in Muzdalifah and collect pebbles for the next rites.",
    ),
    RitualStep(
        sequence_order=5,
        scheduled_day_index=4,
        scheduled_day_label="10th of Dhul-Hijjah",
        ritual_name="Ramy at Aqaba",
        target_node="Jamarat_Complex",
        progress_key="jamrat_aqaba_complete",
        description="Pilgrims perform the stoning at Jamrat al-Aqaba al-Kubra.",
    ),
    RitualStep(
        sequence_order=6,
        scheduled_day_index=4,
        scheduled_day_label="10th of Dhul-Hijjah",
        ritual_name="Sacrifice",
        target_node="Sacrifice_Zone",
        progress_key="sacrifice_complete",
        description="Pilgrims perform the sacrifice following the stoning ritual.",
    ),
    RitualStep(
        sequence_order=7,
        scheduled_day_index=4,
        scheduled_day_label="10th of Dhul-Hijjah",
        ritual_name="Tawaf al-Ifadhah and Sa'y",
        target_node="Tawaf_Area",
        progress_key="ifadhah_sai_complete",
        description="Pilgrims return to the Haram for Tawaf Al-Ifadhah and the Sa'y of Hajj.",
    ),
    RitualStep(
        sequence_order=8,
        scheduled_day_index=5,
        scheduled_day_label="Night of 10th Dhul-Hijjah",
        ritual_name="Night in Mina",
        target_node="Mina_Camps_Core",
        progress_key="first_tashreeq_night_complete",
        description="Pilgrims return to Mina for the first Tashreeq night stay.",
    ),
    RitualStep(
        sequence_order=9,
        scheduled_day_index=6,
        scheduled_day_label="11th of Dhul-Hijjah",
        ritual_name="Mina Stay",
        target_node="Mina_Camps_Core",
        progress_key="mina_day_11_complete",
        description="Pilgrims remain in Mina on the 11th of Dhul-Hijjah.",
    ),
    RitualStep(
        sequence_order=10,
        scheduled_day_index=7,
        scheduled_day_label="12th of Dhul-Hijjah",
        ritual_name="Mina Stay",
        target_node="Mina_Camps_Core",
        progress_key="mina_day_12_complete",
        description="Pilgrims remain in Mina on the 12th of Dhul-Hijjah.",
    ),
    RitualStep(
        sequence_order=11,
        scheduled_day_index=8,
        scheduled_day_label="13th of Dhul-Hijjah",
        ritual_name="Mina Stay",
        target_node="Mina_Camps_Core",
        progress_key="mina_day_13_complete",
        description="Pilgrims remain in Mina on the 13th of Dhul-Hijjah.",
    ),
    RitualStep(
        sequence_order=12,
        scheduled_day_index=9,
        scheduled_day_label="After completing Hajj, usually 12th or 13th",
        ritual_name="Tawaf al-Wadaa",
        target_node="Tawaf_Area",
        progress_key="farewell_tawaf_complete",
        description="Pilgrims complete the farewell circumambulation before departure.",
    ),
)


ROUTE_SEGMENTS: Tuple[Tuple[str, ...], ...] = (
    ("Makkah_Airport", "Makkah_Arrival_Hub", "Masjid_al_Haram_Perimeter"),
    ("Kaaba", "Tawaf_Area", "Masjid_al_Haram_Perimeter", "Sai_Corridor"),
    ("Masjid_al_Haram_Perimeter", "Makkah_Bus_Station", "Aziziyah_Zone"),
    ("Aziziyah_Zone", "Mina_West_Gate", "Mina_Camp_1", "Mina_Camps_Core", "Mina_Camp_2", "Mina_Camp_4", "Mina_East_Gate"),
    ("Mina_Camps_Core", "Jamarat_Bridge", "Jamarat_Complex", "Jamarat"),
    ("Jamarat_Complex", "Sacrifice_Zone", "Mina_Camps_Core"),
    ("Mina_Camps_Core", "Arafat_Gate", "Arafat_Main_Field", "Arafat"),
    ("Arafat_Main_Field", "Muzdalifah_Open_Area", "Muzdalifah"),
    ("Mina_Camps_Core", "Transit_Corridor", "Muzdalifah_Open_Area"),
    ("Mina_Camp_4", "Shade_Corridor", "Shade_Corridor_2", "Cooling_Station_1"),
    ("Mina_Camps_Core", "Medical_Post_1", "Field_Hospital", "Emergency_Point"),
    ("Medical_Post_1", "Emergency_Point_1", "Emergency_Point_2", "Police_Assist_Point"),
    ("Mina_Camps_Core", "Security_Checkpoint_1"),
)

RITUAL_APPROACH_STARTS: Dict[str, str] = {
    "origin_airport_complete": "Makkah_Airport",
    "tawaf_qudoum_complete": "Makkah_Airport",
    "mina_tarwiyah_complete": "Tawaf_Area",
    "arafah_complete": "Mina_Camps_Core",
    "muzdalifah_complete": "Arafat_Main_Field",
    "jamrat_aqaba_complete": "Muzdalifah_Open_Area",
    "sacrifice_complete": "Jamarat_Complex",
    "ifadhah_sai_complete": "Sacrifice_Zone",
    "first_tashreeq_night_complete": "Tawaf_Area",
    "mina_day_11_complete": "Mina_Camps_Core",
    "mina_day_12_complete": "Mina_Camps_Core",
    "mina_day_13_complete": "Mina_Camps_Core",
    "farewell_tawaf_complete": "Mina_Camps_Core",
}


def get_simulation_day_slot(day_index: int) -> SimulationDaySlot:
    bounded_index = min(max(int(day_index), 0), len(HAJJ_DAY_SLOTS) - 1)
    return HAJJ_DAY_SLOTS[bounded_index]


def get_pending_ritual_step(ritual_progress: Sequence[str]) -> Optional[RitualStep]:
    completed = set(ritual_progress)
    for step in HAJJ_RITUAL_SCHEDULE:
        if step.progress_key not in completed:
            return step
    return None


def get_completed_ritual_steps(ritual_progress: Sequence[str]) -> List[RitualStep]:
    completed = set(ritual_progress)
    return [step for step in HAJJ_RITUAL_SCHEDULE if step.progress_key in completed]


def get_following_ritual_step(ritual_progress: Sequence[str]) -> Optional[RitualStep]:
    pending_step = get_pending_ritual_step(ritual_progress)
    if pending_step is None:
        return None

    found_pending = False
    for step in HAJJ_RITUAL_SCHEDULE:
        if found_pending:
            return step
        if step.progress_key == pending_step.progress_key:
            found_pending = True
    return None


def get_ritual_schedule_payload() -> List[dict]:
    return [
        {
            "sequence_order": step.sequence_order,
            "scheduled_day_index": step.scheduled_day_index,
            "scheduled_day_label": step.scheduled_day_label,
            "ritual_name": step.ritual_name,
            "target_node": step.target_node,
            "progress_key": step.progress_key,
            "description": step.description,
        }
        for step in HAJJ_RITUAL_SCHEDULE
    ]


def get_simulation_day_payload() -> List[dict]:
    return [
        {
            "day_index": slot.day_index,
            "label": slot.label,
            "rituals": list(slot.rituals),
        }
        for slot in HAJJ_DAY_SLOTS
    ]


def get_simulation_ritual_step(tick: int) -> RitualStep:
    bounded_index = min(max(int(tick), 0), len(HAJJ_RITUAL_SCHEDULE) - 1)
    return HAJJ_RITUAL_SCHEDULE[bounded_index]


def get_next_simulation_ritual_step(tick: int) -> Optional[RitualStep]:
    next_index = int(tick) + 1
    if next_index < 0 or next_index >= len(HAJJ_RITUAL_SCHEDULE):
        return None
    return HAJJ_RITUAL_SCHEDULE[next_index]


def get_simulation_tick_payload(tick: int) -> dict:
    if int(tick) < 0:
        first_step = HAJJ_RITUAL_SCHEDULE[0]
        return {
            "simulation_ritual_index": -1,
            "simulation_day_index": first_step.scheduled_day_index,
            "simulation_day_label": first_step.scheduled_day_label,
            "current_ritual": "Not Started",
            "next_ritual": first_step.ritual_name,
            "next_ritual_day_label": first_step.scheduled_day_label,
            "day_plan_rituals": [first_step.ritual_name],
        }

    bounded_tick = max(int(tick), 0)
    if bounded_tick >= len(HAJJ_RITUAL_SCHEDULE):
        return {
            "simulation_ritual_index": len(HAJJ_RITUAL_SCHEDULE),
            "simulation_day_index": HAJJ_DAY_SLOTS[-1].day_index,
            "simulation_day_label": "Completed",
            "current_ritual": "Hajj Complete",
            "next_ritual": "Completed",
            "next_ritual_day_label": "Completed",
            "day_plan_rituals": [],
        }

    current_step = get_simulation_ritual_step(bounded_tick)
    next_step = get_next_simulation_ritual_step(bounded_tick)
    day_slot = get_simulation_day_slot(current_step.scheduled_day_index)
    return {
        "simulation_ritual_index": bounded_tick,
        "simulation_day_index": current_step.scheduled_day_index,
        "simulation_day_label": current_step.scheduled_day_label,
        "current_ritual": current_step.ritual_name,
        "next_ritual": next_step.ritual_name if next_step else "Completed",
        "next_ritual_day_label": next_step.scheduled_day_label if next_step else "Completed",
        "day_plan_rituals": list(day_slot.rituals),
    }


def build_ritual_day_label(step: RitualStep) -> str:
    return step.scheduled_day_label


def _build_route_graph() -> Dict[str, List[str]]:
    graph: Dict[str, List[str]] = {}
    for segment in ROUTE_SEGMENTS:
        for left, right in zip(segment, segment[1:]):
            graph.setdefault(left, []).append(right)
            graph.setdefault(right, []).append(left)
    return graph


ROUTE_GRAPH = _build_route_graph()


def plan_route(current_node: str, destination: str) -> List[str]:
    if current_node == destination:
        return [current_node]
    if current_node not in ROUTE_GRAPH or destination not in ROUTE_GRAPH:
        return [current_node, destination]

    frontier: deque[Tuple[str, List[str]]] = deque([(current_node, [current_node])])
    visited = {current_node}

    while frontier:
        node, path = frontier.popleft()
        for neighbor in ROUTE_GRAPH.get(node, []):
            if neighbor in visited:
                continue
            next_path = path + [neighbor]
            if neighbor == destination:
                return next_path
            visited.add(neighbor)
            frontier.append((neighbor, next_path))

    return [current_node, destination]


def get_ritual_approach_route(step: RitualStep) -> List[str]:
    start_node = RITUAL_APPROACH_STARTS.get(step.progress_key, step.target_node)
    return plan_route(start_node, step.target_node)


def get_reasonable_nodes_for_step(step: RitualStep) -> List[str]:
    return [step.target_node]


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
    ritual_day_index: int = -1
    ritual_day_label: str = "Upon Arrival in Makkah"
    current_ritual: str = "Not Started"
    next_ritual: str = "Tawaf Al-Qudoum (Arrival Tawaf)"
    next_ritual_day_label: str = "Upon Arrival in Makkah"
    ritual_window_open: bool = False
    active_route: List[str] = field(default_factory=list)


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
    ritual_schedule: List[dict] = field(default_factory=get_ritual_schedule_payload)


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
        hazard = environment_data.get("hazard")

        if state.is_panicking and state.stress < 88.0 and state.hydration > 45.0:
            return "REST"

        # Panic is now a severe condition, not the default stress response.
        if state.stress >= 95.0 and (float(environment_data.get("density", 0.0)) >= 8.0 or hazard):
            return "ENTER_PANIC_MODE"

        if state.fatigue >= 75.0 or state.hydration <= 30.0:
            return "REST"

        if state.stress >= 80.0:
            return "AVOID_CROWD"

        if not state.is_with_group and social.group_last_seen_node and state.stress >= 70.0:
            return f"MOVE_TO_{social.group_last_seen_node}"

        if not state.ritual_window_open:
            return "WAIT_FOR_RITUAL_WINDOW"

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
        self.start_node = initial_node
        self.state = DynamicState(current_node=initial_node, target_node=target_node)
        self.memory = Memory()
        self.brain = BehaviorEngine(self, llm_override=llm_override)
        self._sync_ritual_goal({"simulation_ritual_index": -1})

    def step(self, environment_data: dict) -> str:
        self.state.simulation_tick += 1
        self._sync_ritual_goal(environment_data)
        self._mark_completed_rituals_before_current_tick(environment_data)
        self._perceive_environment(environment_data)
        action = self.brain.decide_action(environment_data)
        self._execute_action(action, environment_data)
        self._update_ritual_progress(environment_data)
        self._sync_ritual_goal(environment_data)
        return action

    def reset_ritual_cycle(self) -> None:
        preserved_progress = [
            progress for progress in self.memory.long_term.ritual_progress
            if progress == "arrival_registered"
        ]
        self.memory.long_term.ritual_progress = preserved_progress
        self.state.current_node = self.start_node
        self.state.active_route = [self.start_node]
        self._sync_ritual_goal({"simulation_ritual_index": -1})
        self.memory.short_term.remember_event("Ritual schedule reset to start")

    def sync_with_environment(self, environment_data: dict) -> None:
        self._mark_completed_rituals_before_current_tick(environment_data)
        self._sync_ritual_goal(environment_data)

    def _sync_ritual_goal(self, environment_data: dict) -> None:
        simulation_ritual_index = int(
            environment_data.get(
                "simulation_ritual_index",
                environment_data.get("ritual_day_index", 0),
            )
        )

        if simulation_ritual_index < 0:
            first_step = HAJJ_RITUAL_SCHEDULE[0]
            self.state.ritual_day_index = -1
            self.state.ritual_day_label = first_step.scheduled_day_label
            self.state.current_ritual = "Not Started"
            self.state.next_ritual = first_step.ritual_name
            self.state.next_ritual_day_label = first_step.scheduled_day_label
            self.state.target_node = first_step.target_node
            self.state.ritual_window_open = False
            self.state.active_route = [self.state.current_node]
        elif simulation_ritual_index >= len(HAJJ_RITUAL_SCHEDULE):
            self.state.ritual_day_index = len(HAJJ_RITUAL_SCHEDULE) - 1
            self.state.ritual_day_label = "Completed"
            self.state.current_ritual = "Hajj Complete"
            self.state.next_ritual = "Completed"
            self.state.next_ritual_day_label = "Completed"
            self.state.target_node = self.state.current_node
            self.state.ritual_window_open = False
            self.state.active_route = []
        else:
            step = get_simulation_ritual_step(simulation_ritual_index)
            following_step = get_next_simulation_ritual_step(simulation_ritual_index)
            self.state.ritual_window_open = True
            self.state.ritual_day_index = step.sequence_order - 1
            self.state.ritual_day_label = build_ritual_day_label(step)
            self.state.current_ritual = step.ritual_name
            self.state.target_node = step.target_node
            self.state.next_ritual = following_step.ritual_name if following_step else "Completed"
            self.state.next_ritual_day_label = following_step.scheduled_day_label if following_step else "Completed"

        if not self.memory.long_term.ritual_schedule:
            self.memory.long_term.ritual_schedule = get_ritual_schedule_payload()

    def _mark_completed_rituals_before_current_tick(self, environment_data: dict) -> None:
        simulation_ritual_index = int(
            environment_data.get(
                "simulation_ritual_index",
                environment_data.get("ritual_day_index", 0),
            )
        )
        for step in HAJJ_RITUAL_SCHEDULE:
            if (step.sequence_order - 1) >= simulation_ritual_index:
                break
            if step.progress_key not in self.memory.long_term.ritual_progress:
                self.memory.long_term.ritual_progress.append(step.progress_key)

    def _update_ritual_progress(self, environment_data: Optional[dict] = None) -> None:
        if not self.state.ritual_window_open:
            return
        if environment_data is None:
            step = get_pending_ritual_step(self.memory.long_term.ritual_progress)
        else:
            simulation_ritual_index = int(
                environment_data.get(
                    "simulation_ritual_index",
                    environment_data.get("ritual_day_index", 0),
                )
            )
            if simulation_ritual_index < 0 or simulation_ritual_index >= len(HAJJ_RITUAL_SCHEDULE):
                return
            step = get_simulation_ritual_step(simulation_ritual_index)
        if step is None:
            return
        if self.state.current_node != step.target_node:
            return
        if step.progress_key in self.memory.long_term.ritual_progress:
            return
        self.memory.long_term.ritual_progress.append(step.progress_key)
        self.memory.short_term.remember_event(f"Completed ritual: {step.ritual_name}")

    def _align_location_with_ritual(self, force: bool = False) -> None:
        destination = self.state.target_node
        if not destination:
            return

        if not force and self.state.current_node == destination:
            self.memory.long_term.known_routes[destination] = [destination]
            return

        self.state.current_node = destination
        self.state.active_route = [destination]
        self.memory.long_term.known_routes[destination] = [destination]

    def _resolve_route(self, destination: str) -> List[str]:
        remembered_route = list(self.memory.long_term.known_routes.get(destination, []))
        if remembered_route and destination in remembered_route and self.state.current_node in remembered_route:
            current_index = remembered_route.index(self.state.current_node)
            destination_index = remembered_route.index(destination)
            if current_index <= destination_index:
                return remembered_route[current_index:destination_index + 1]

        planned_route = plan_route(self.state.current_node, destination)
        self.memory.long_term.known_routes[destination] = planned_route
        return planned_route

    def _move_one_hop(self, destination: str) -> None:
        self.state.current_node = destination
        self.state.active_route = [destination]
        self.memory.long_term.known_routes[destination] = [destination]

    def _perceive_environment(self, environment_data: dict) -> None:
        density = float(environment_data.get("density", 0.0))
        temperature = float(environment_data.get("temperature", 32.0))
        hazard = environment_data.get("hazard")
        visible_group_node = environment_data.get("group_location")
        group_locations = environment_data.get("group_locations")

        # Each tick now represents a long ritual/day window, so baseline exposure
        # should wear pilgrims down more than a short real-time step.
        stress_gain = max(0.0, density - 4.0) * 1.7 + max(0.0, temperature - 36.0) * 0.45
        fatigue_gain = max(1.2, 2.2 - self.profile.mobility) + max(0.0, temperature - 34.0) * 0.24
        hydration_loss = max(4.5, (temperature - 28.0) * 0.45 + 2.2)

        if self.profile.health_status.lower() != "stable":
            fatigue_gain += 0.9
            stress_gain += 2.4

        if self.state.is_with_group:
            stress_gain = max(0.0, stress_gain - 1.0)
        else:
            stress_gain += 2.0

        if density >= 6.0:
            hydration_loss += 0.8

        if group_locations and self.profile.group_id in group_locations:
            from collections import Counter
            group_nodes = group_locations[self.profile.group_id]
            if group_nodes:
                most_common_node, _ = Counter(group_nodes).most_common(1)[0]
                if self.state.current_node != most_common_node:
                    # Increase stress more if away from group majority
                    stress_gain += 2.5

        if hazard:
            hazard_stress_boost = {
                "stampede_risk": 3.0,
                "crowd_bottleneck": 2.4,
                "extreme_heat": 2.2,
                "medical_overload": 2.0,
                "route_closure": 1.9,
                "transport_delay": 1.4,
                "lost_group_member": 1.8,
                "heat_stress": 2.1,
                "medical_incident": 1.6,
                "route_congestion": 1.7,
            }.get(str(hazard), 1.2)
            stress_gain += hazard_stress_boost

            hydration_hazard_boost = {
                "extreme_heat": 2.2,
                "heat_stress": 1.8,
                "crowd_bottleneck": 1.0,
                "stampede_risk": 1.0,
                "route_congestion": 0.8,
                "transport_delay": 0.8,
            }.get(str(hazard), 0.4)
            hydration_loss += hydration_hazard_boost

        self.state.stress = min(100.0, self.state.stress + stress_gain)
        self.state.fatigue = min(100.0, self.state.fatigue + fatigue_gain)
        self.state.hydration = max(0.0, self.state.hydration - hydration_loss)

        panic_threshold = 96.0
        panic_threshold -= self.profile.risk_tolerance * 6.0
        if self.profile.health_status == "needs_support":
            panic_threshold -= 2.0
        elif self.profile.health_status == "high_risk":
            panic_threshold -= 4.0
        if hazard in {"stampede_risk", "crowd_bottleneck"}:
            panic_threshold -= 3.0

        self.state.is_panicking = (
            self.state.stress >= panic_threshold
            and self.state.hydration <= 55.0
            and density >= 6.0
        )

        if hazard:
            self.memory.long_term.known_hazards[self.state.current_node] = str(hazard)
            self.memory.short_term.remember_event(f"Hazard seen: {hazard}")

        if group_locations and self.profile.group_id in group_locations:
            from collections import Counter
            group_nodes = group_locations[self.profile.group_id]
            if group_nodes:
                most_common_node, _ = Counter(group_nodes).most_common(1)[0]
                self.memory.social.group_last_seen_node = most_common_node
                self.state.is_with_group = most_common_node == self.state.current_node
                return

        if visible_group_node:
            self.memory.social.group_last_seen_node = visible_group_node
            self.state.is_with_group = visible_group_node == self.state.current_node

    def _apply_travel_load(
        self,
        destination: str,
        environment_data: dict,
        load_multiplier: float = 1.0,
        stress_relief: float = 0.0,
    ) -> None:
        route = self._resolve_route(destination)
        hops = max(0, len(route) - 1)
        if hops <= 0:
            self._move_one_hop(destination)
            return

        temperature = float(environment_data.get("temperature", 32.0))
        density = float(environment_data.get("density", 0.0))
        hazard = str(environment_data.get("hazard") or "")
        mobility_penalty = max(0.0, 1.0 - self.profile.mobility)

        travel_hydration_loss = (
            (2.1 * hops) +
            (mobility_penalty * 5.0) +
            max(0.0, temperature - 35.0) * 0.25
        ) * load_multiplier
        travel_fatigue_gain = (
            (1.6 * hops) +
            (mobility_penalty * 4.5) +
            max(0.0, temperature - 34.0) * 0.16
        ) * load_multiplier
        travel_stress_gain = (
            (1.0 * hops) +
            max(0.0, density - 5.0) * 0.7
        ) * load_multiplier

        if hazard in {"extreme_heat", "heat_stress"}:
            travel_hydration_loss += 1.4 * load_multiplier
        if hazard in {"crowd_bottleneck", "stampede_risk", "route_congestion"}:
            travel_stress_gain += 1.3 * load_multiplier

        self.state.hydration = max(0.0, self.state.hydration - travel_hydration_loss)
        self.state.fatigue = min(100.0, self.state.fatigue + travel_fatigue_gain)
        self.state.stress = min(100.0, max(0.0, self.state.stress + travel_stress_gain - stress_relief))
        self.state.current_node = destination
        self.state.active_route = route
        self.memory.long_term.known_routes[destination] = route

    def _execute_action(self, action: str, environment_data: dict) -> None:
        self.memory.short_term.remember_node(self.state.current_node)
        self.memory.short_term.remember_event(f"Tick {self.state.simulation_tick}: {action}")
        self.state.last_action = action

        if action == "WAIT_FOR_RITUAL_WINDOW":
            self.state.active_route = []
            self.state.stress = max(0.0, self.state.stress - 2.0)
            return

        if action == "REST":
            self.state.fatigue = max(0.0, self.state.fatigue - 12.0)
            self.state.stress = max(0.0, self.state.stress - 9.0)
            self.state.hydration = min(100.0, self.state.hydration + 14.0)
            if self.state.stress < 85.0 and self.state.hydration > 45.0:
                self.state.is_panicking = False
            return

        if action == "AVOID_CROWD":
            alternate_node = environment_data.get("alternate_node", self.state.current_node)
            self._apply_travel_load(
                alternate_node,
                environment_data,
                load_multiplier=0.85,
                stress_relief=6.0,
            )
            return

        if action == "ENTER_PANIC_MODE":
            self.state.is_panicking = True
            panic_node = environment_data.get("panic_node", self.state.current_node)
            self._apply_travel_load(
                panic_node,
                environment_data,
                load_multiplier=1.35,
            )
            return

        if action.startswith("MOVE_TO_"):
            destination = action.replace("MOVE_TO_", "", 1)
            self._apply_travel_load(destination, environment_data)

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
                "ritual_day_index": self.state.ritual_day_index,
                "ritual_day_label": self.state.ritual_day_label,
                "current_ritual": self.state.current_ritual,
                "next_ritual": self.state.next_ritual,
                "next_ritual_day_label": self.state.next_ritual_day_label,
                "ritual_window_open": self.state.ritual_window_open,
                "active_route": self.state.active_route,
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
                    "ritual_schedule": self.memory.long_term.ritual_schedule,
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
        ("Saudi Arabia", "Arabic"),
        ("Indonesian", "Bahasa Indonesia"),
        ("Pakistani", "Urdu"),
        ("Indian", "Hindi"),
        ("Bangladeshi", "Bengali"),
        ("Egyptian", "Arabic"),
        ("Nigerian", "English"),
        ("Turkish", "Turkish"),
        ("Malaysian", "Malay"),
        ("Moroccan", "Arabic"),
    )
    DEFAULT_INITIAL_NODES: Sequence[str] = (
        "Makkah_Airport",
    )
    DEFAULT_TARGET_NODES: Sequence[str] = (
        "Makkah_Airport",
        "Makkah_Arrival_Hub",
        "Tawaf_Area",
        "Sai_Corridor",
        "Mina_Camps_Core",
        "Sacrifice_Zone",
        "Jamarat_Complex",
        "Arafat_Main_Field",
        "Muzdalifah_Open_Area",
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
        age = self.random.randint(18, 90)
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
        preferred_route = plan_route(agent.state.current_node, agent.state.target_node)
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
    agent.memory.long_term.ritual_schedule = long_term_memory.get(
        "ritual_schedule",
        get_ritual_schedule_payload(),
    )
    agent._sync_ritual_goal({"simulation_ritual_index": -1})

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
