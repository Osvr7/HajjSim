"""Hamlah (Hajj campaign) and support-unit models for HajjSim.

A Hamlah groups pilgrim agents under a single campaign operator and carries
the staggered dispatch offset used by the time engine in ``hajj_agents.py``.
Support units (buses, marshals, police, ambulances) are lightweight reactive
agents defined separately from the four-layer ``PilgrimAgent`` model, since
they don't need memory or a behavior engine -- just simple per-tick rules.
"""

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# One-way dependency only (hajj_agents.py never imports this module), so this
# stays acyclic.
from hajj_agents import corridor_ticks, next_hop_zone, zone_of

# Successive Hamlahs (by seed order) start moving this many simulated minutes
# apart, so campaigns dispatch in staggered waves instead of all at once.
# Bumped from round 1's 30.0 now that a tick is 60 simulated minutes instead
# of 20 -- a 30-minute stagger would otherwise be invisible (sub-tick).
STAGGER_INTERVAL_MINUTES = 90.0


@dataclass
class Hamlah:
    """One Hajj campaign: a pilgrim group traveling under a single operator.

    Every Hamlah has a fixed nationality (every member must match it -- see
    HamlahRegistry.nationality_to_hamlah_id) and a designated base camp,
    which is a real Hotel object (base_camp_hotel_id) rather than a raw
    coordinate.
    """

    hamlah_id: str
    name: str
    manager_name: str
    declared_pilgrim_count: int
    nationality: str
    base_camp_hotel_id: str
    dispatch_offset_minutes: float = 0.0
    member_ids: List[str] = field(default_factory=list)

    def to_payload(self) -> dict:
        """Convert to a JSON-friendly dict, including the live member count."""
        # declared_pilgrim_count is the operator's registered capacity;
        # actual_pilgrim_count reflects who is really assigned right now.
        return {
            "hamlah_id": self.hamlah_id,
            "name": self.name,
            "manager_name": self.manager_name,
            "declared_pilgrim_count": self.declared_pilgrim_count,
            "actual_pilgrim_count": len(self.member_ids),
            "nationality": self.nationality,
            "base_camp_hotel_id": self.base_camp_hotel_id,
            "dispatch_offset_minutes": self.dispatch_offset_minutes,
            "member_ids": list(self.member_ids),
        }


# A pilgrim's raw nationality string doesn't always exactly match a Hamlah's
# canonical nationality (e.g. seed data has "Saudi" where AgentFactory's
# canonical list says "Saudi Arabia") -- this normalizes both sides before
# comparing, instead of editing pilgrim identity data to force an exact match.
NATIONALITY_ALIASES: Dict[str, str] = {
    "saudi": "saudi arabia",
}


def normalize_nationality(value: str) -> str:
    """Canonicalize a nationality string for matching purposes only."""
    lowered = (value or "").strip().lower()
    return NATIONALITY_ALIASES.get(lowered, lowered)


class HamlahRegistry:
    """Loads Hamlah seed records from disk and tracks live pilgrim membership."""

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.hamlahs: Dict[str, Hamlah] = {}
        self.load()

    def load(self) -> None:
        """Read seed Hamlah records, assigning staggered dispatch offsets in seed order."""
        self.hamlahs = {}
        if not self.data_file.exists():
            return

        with self.data_file.open("r", encoding="utf-8") as file:
            records = json.load(file)

        for index, record in enumerate(records):
            hamlah = Hamlah(
                hamlah_id=record["hamlah_id"],
                name=record["name"],
                manager_name=record["manager_name"],
                declared_pilgrim_count=int(record.get("declared_pilgrim_count", 0)),
                nationality=record["nationality"],
                base_camp_hotel_id=record["base_camp_hotel_id"],
                dispatch_offset_minutes=index * STAGGER_INTERVAL_MINUTES,
            )
            self.hamlahs[hamlah.hamlah_id] = hamlah

    def list_hamlahs(self) -> List[dict]:
        """Return every Hamlah as a JSON-ready payload."""
        return [hamlah.to_payload() for hamlah in self.hamlahs.values()]

    def get_dispatch_offsets(self) -> Dict[str, float]:
        """Return a hamlah_id -> dispatch_offset_minutes map for the step loop."""
        return {hamlah_id: hamlah.dispatch_offset_minutes for hamlah_id, hamlah in self.hamlahs.items()}

    def nationality_to_hamlah_id(self) -> Dict[str, str]:
        """Map each (normalized) nationality to its one matching Hamlah.

        Keyed by the *raw* nationality string as it would appear on a
        pilgrim record (e.g. AgentFactory.DEFAULT_NATIONALITIES), so callers
        can look up with `mapping[pilgrim_nationality]` directly. If two
        Hamlahs somehow shared a nationality, the last one loaded wins --
        the seed data is designed to keep this 1:1.
        """
        mapping: Dict[str, str] = {}
        for hamlah in self.hamlahs.values():
            mapping[hamlah.nationality] = hamlah.hamlah_id
        return mapping

    def find_hamlah_for_nationality(self, nationality: str) -> Optional[Hamlah]:
        """Find the Hamlah whose nationality matches, normalizing both sides."""
        target = normalize_nationality(nationality)
        for hamlah in self.hamlahs.values():
            if normalize_nationality(hamlah.nationality) == target:
                return hamlah
        return None

    def assign_pilgrim(self, hamlah_id: Optional[str], pilgrim_id: str) -> None:
        """Record that a pilgrim belongs to the given Hamlah, if it exists."""
        hamlah = self.hamlahs.get(hamlah_id) if hamlah_id else None
        if hamlah and pilgrim_id not in hamlah.member_ids:
            hamlah.member_ids.append(pilgrim_id)

    def clear_membership(self) -> None:
        """Reset all member lists before re-deriving them from the agent roster."""
        for hamlah in self.hamlahs.values():
            hamlah.member_ids = []

    def rebuild_membership(self, pilgrim_hamlah_pairs: Iterable[Tuple[str, Optional[str]]]) -> None:
        """Recompute every Hamlah's member list from (pilgrim_id, hamlah_id) pairs."""
        self.clear_membership()
        for pilgrim_id, hamlah_id in pilgrim_hamlah_pairs:
            self.assign_pilgrim(hamlah_id, pilgrim_id)


# ============================================================
# Hotels
# ------------------------------------------------------------
# A Hamlah's base camp is a real Hotel object: a capacity-based
# container pilgrims check into. The frontend hides individual pilgrim
# markers while checked in and shows a live occupancy badge instead.
# ============================================================


@dataclass
class Hotel:
    """A capacity-based lodging node -- also a Hamlah's designated base camp."""

    hotel_id: str
    name: str
    node_id: str
    capacity: int
    occupant_ids: List[str] = field(default_factory=list)

    def to_payload(self) -> dict:
        """Convert to a JSON-friendly dict, including live occupancy."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "node_id": self.node_id,
            "capacity": self.capacity,
            "occupancy": len(self.occupant_ids),
            "occupant_ids": list(self.occupant_ids),
        }


class HotelRegistry:
    """Loads Hotel seed records from disk and tracks live pilgrim occupancy."""

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.hotels: Dict[str, Hotel] = {}
        self.load()

    def load(self) -> None:
        """Read seed Hotel records from disk."""
        self.hotels = {}
        if not self.data_file.exists():
            return

        with self.data_file.open("r", encoding="utf-8") as file:
            records = json.load(file)

        for record in records:
            hotel = Hotel(
                hotel_id=record["hotel_id"],
                name=record["name"],
                node_id=record["node_id"],
                capacity=int(record.get("capacity", 0)),
            )
            self.hotels[hotel.hotel_id] = hotel

    def list_hotels(self) -> List[dict]:
        """Return every hotel as a JSON-ready payload."""
        return [hotel.to_payload() for hotel in self.hotels.values()]

    def check_in(self, hotel_id: Optional[str], pilgrim_id: str) -> None:
        """Record that a pilgrim is currently checked in at the given hotel."""
        hotel = self.hotels.get(hotel_id) if hotel_id else None
        if hotel and pilgrim_id not in hotel.occupant_ids:
            hotel.occupant_ids.append(pilgrim_id)

    def check_out(self, hotel_id: Optional[str], pilgrim_id: str) -> None:
        """Remove a pilgrim from a hotel's occupant list, if present."""
        hotel = self.hotels.get(hotel_id) if hotel_id else None
        if hotel and pilgrim_id in hotel.occupant_ids:
            hotel.occupant_ids.remove(pilgrim_id)

    def clear_occupancy(self) -> None:
        """Reset all occupant lists before re-deriving them from the agent roster."""
        for hotel in self.hotels.values():
            hotel.occupant_ids = []

    def rebuild_occupancy(self, pilgrim_hotel_pairs: Iterable[Tuple[str, Optional[str]]]) -> None:
        """Recompute every hotel's occupant list from (pilgrim_id, hotel_id) pairs."""
        self.clear_occupancy()
        for pilgrim_id, hotel_id in pilgrim_hotel_pairs:
            self.check_in(hotel_id, pilgrim_id)


# ============================================================
# Heterogeneous support units
# ------------------------------------------------------------
# Buses, marshals, police, and ambulances are lightweight reactive
# agents -- no memory or behavior engine, just a small per-tick rule
# specific to their role. They still expose current_node/target_node
# so the frontend can plot them the same way as pilgrim markers.
# ============================================================


def _is_urgent(pilgrim_snapshot: dict) -> bool:
    """Flag a pilgrim as needing ambulance attention (panicking or high-risk).

    A pilgrim who is boarded on a bus, queued for one, or checked into a
    hotel isn't reachable at a map node the normal way, so it's excluded
    even if its vitals would otherwise qualify.
    """
    state = pilgrim_snapshot["state"]
    if state.get("travel_state", "PEDESTRIAN") != "PEDESTRIAN":
        return False
    if state.get("is_panicking"):
        return True
    stress = float(state.get("stress", 0))
    fatigue = float(state.get("fatigue", 0))
    hydration = float(state.get("hydration", 100))
    return stress >= 88 or fatigue >= 86 or hydration <= 28


@dataclass
class OperationalUnit:
    """Shared fields for every non-pilgrim support unit on the map."""

    unit_id: str
    unit_type: str  # "bus" | "marshal" | "police" | "ambulance"
    current_node: str
    target_node: str
    status: str = "idle"
    assigned_hamlah_id: Optional[str] = None
    last_action: str = "idle"
    is_manually_deployed: bool = False

    def step(self, environment_data: dict, pilgrim_snapshots: List[dict]) -> str:
        """Default no-op step; every subclass overrides this with real logic."""
        self.last_action = "idle"
        return self.last_action

    def to_payload(self) -> dict:
        """Convert the shared fields to a JSON-friendly dict."""
        return {
            "unit_id": self.unit_id,
            "unit_type": self.unit_type,
            "current_node": self.current_node,
            "target_node": self.target_node,
            "status": self.status,
            "assigned_hamlah_id": self.assigned_hamlah_id,
            "last_action": self.last_action,
            "is_manually_deployed": self.is_manually_deployed,
        }


@dataclass
class BusUnit(OperationalUnit):
    """A support unit that moves pilgrims between zones.

    Corridor buses (is_corridor_bus=True, the default) serve a fixed
    inter-city corridor as a shared fleet -- not owned by any Hamlah -- and
    are entirely driven by ConvoyDispatchCoordinator: it boards waiting
    cohorts, advances transit_progress across multiple ticks, and disembarks
    them on arrival. This class's own step() is a no-op for those buses.

    The one legacy bus (is_corridor_bus=False) keeps round 1's original
    cyclic local-loop behavior for cosmetic intra-zone flavor.
    """

    passenger_capacity: int = 40
    is_corridor_bus: bool = True

    # -- Corridor bus fields (ConvoyDispatchCoordinator-owned) --
    corridor_zone_a: str = ""
    corridor_zone_b: str = ""
    stop_a_node: str = ""
    stop_b_node: str = ""
    manifest: List[str] = field(default_factory=list)
    transit_from_node: str = ""
    transit_to_node: str = ""
    transit_ticks_required: int = 1
    transit_ticks_elapsed: int = 0
    transit_progress: float = 0.0
    direction_forward: bool = True
    idle_ticks_at_stop: int = 0

    # -- Legacy local-loop fields (BUS_LOCAL only) --
    assigned_route: List[str] = field(default_factory=list)
    route_position: int = 0

    def step(self, environment_data: dict, pilgrim_snapshots: List[dict]) -> str:
        if self.is_corridor_bus:
            # Fully owned by ConvoyDispatchCoordinator -- see app.py's step
            # ordering, which calls it before this per-unit step loop runs.
            return self.last_action

        if not self.assigned_route:
            self.last_action = "idle"
            return self.last_action

        # Advance one stop every other tick so the local bus visibly travels
        # instead of teleporting every simulation step.
        tick = int(environment_data.get("tick", 0))
        if tick % 2 == 0:
            self.route_position = (self.route_position + 1) % len(self.assigned_route)
            self.current_node = self.assigned_route[self.route_position]
            next_index = (self.route_position + 1) % len(self.assigned_route)
            self.target_node = self.assigned_route[next_index]
            self.status = "in_transit"
            self.last_action = f"SHUTTLE_TO_{self.current_node}"
        else:
            self.status = "at_stop"
            self.last_action = "HOLDING_AT_STOP"
        return self.last_action

    def to_payload(self) -> dict:
        payload = super().to_payload()
        payload.update({
            "passenger_capacity": self.passenger_capacity,
            "is_corridor_bus": self.is_corridor_bus,
            "corridor_zone_a": self.corridor_zone_a,
            "corridor_zone_b": self.corridor_zone_b,
            "manifest_count": len(self.manifest),
            "transit_from_node": self.transit_from_node,
            "transit_to_node": self.transit_to_node,
            "transit_progress": round(self.transit_progress, 3),
            "assigned_route": list(self.assigned_route),
            "route_position": self.route_position,
        })
        return payload


class ConvoyDispatchCoordinator:
    """Owns all real corridor-bus movement: arrival/disembark, then boarding.

    Runs once per tick, after pilgrims have decided their own actions (so it
    sees freshly-set AWAITING_TRANSPORT states) and before marshal/police/
    ambulance stepping (so, e.g., an ambulance doesn't try to reach a pilgrim
    who just boarded a bus this same tick).
    """

    # A bus that finds nothing to board waits this many ticks before
    # dispatching empty, so it doesn't freeze at a stop forever.
    MAX_IDLE_TICKS_BEFORE_EMPTY_DISPATCH = 2

    def step(self, agents: Dict[str, object], units: Dict[str, "OperationalUnit"], tick: int) -> List[dict]:
        """Advance every corridor bus one tick; returns a list of event dicts."""
        buses = [unit for unit in units.values() if isinstance(unit, BusUnit) and unit.is_corridor_bus]
        events = self._advance_transit_and_disembark(agents, buses)
        events += self._board_waiting_cohorts(agents, buses)
        return events

    def _advance_transit_and_disembark(self, agents: Dict[str, object], buses: List["BusUnit"]) -> List[dict]:
        events: List[dict] = []
        for bus in buses:
            if bus.status != "in_transit":
                continue
            bus.transit_ticks_elapsed += 1
            bus.transit_progress = min(1.0, bus.transit_ticks_elapsed / max(1, bus.transit_ticks_required))
            if bus.transit_ticks_elapsed < bus.transit_ticks_required:
                bus.last_action = f"IN_TRANSIT_TO_{bus.transit_to_node}"
                continue

            arrival_node = bus.transit_to_node
            bus.current_node = arrival_node
            bus.target_node = arrival_node
            bus.status = "at_stop"
            bus.direction_forward = not bus.direction_forward
            bus.idle_ticks_at_stop = 0
            bus.last_action = f"ARRIVED_AT_{arrival_node}"
            for pilgrim_id in bus.manifest:
                agent = agents.get(pilgrim_id)
                if agent is None:
                    continue
                agent.state.current_node = arrival_node
                agent.state.travel_state = "PEDESTRIAN"
                agent.state.boarded_unit_id = None
            events.append({
                "event": "bus_arrived", "unit_id": bus.unit_id,
                "node": arrival_node, "passenger_count": len(bus.manifest),
            })
            bus.manifest = []
        return events

    def _board_waiting_cohorts(self, agents: Dict[str, object], buses: List["BusUnit"]) -> List[dict]:
        events: List[dict] = []

        # Group every queued pilgrim by the corridor it needs, oldest-first
        # within each Hamlah so cohorts board together (FIFO, starvation-free).
        waiting_by_corridor: Dict[Tuple[str, str], List[object]] = {}
        for agent in agents.values():
            if agent.state.travel_state != "AWAITING_TRANSPORT":
                continue
            from_zone = zone_of(agent.state.current_node)
            final_zone = zone_of(agent.state.target_node)
            if from_zone == final_zone:
                continue
            # The destination zone may not have a direct bus corridor (e.g.
            # Haram -> Arafat) -- queue for the next hop on the shortest
            # corridor path instead; arriving there re-triggers AWAITING_
            # TRANSPORT for the following hop until the final zone is reached.
            to_zone = next_hop_zone(from_zone, final_zone)
            if to_zone is None:
                continue
            waiting_by_corridor.setdefault((from_zone, to_zone), []).append(agent)
        for corridor_agents in waiting_by_corridor.values():
            corridor_agents.sort(key=lambda a: (a.profile.hamlah_id or "", a.state.awaiting_since_tick))

        for bus in buses:
            if bus.status != "at_stop":
                continue

            if bus.current_node == bus.stop_a_node:
                from_zone, to_zone, to_node = bus.corridor_zone_a, bus.corridor_zone_b, bus.stop_b_node
            else:
                from_zone, to_zone, to_node = bus.corridor_zone_b, bus.corridor_zone_a, bus.stop_a_node

            queue = waiting_by_corridor.get((from_zone, to_zone), [])
            boarded: List[str] = []
            remaining_capacity = bus.passenger_capacity
            while queue and remaining_capacity > 0:
                agent = queue[0]
                agent.state.travel_state = "IN_TRANSIT"
                agent.state.boarded_unit_id = bus.unit_id
                boarded.append(agent.profile.pilgrim_id)
                remaining_capacity -= 1
                # Pop from the shared queue so a second bus on this corridor
                # this same tick doesn't double-board the same pilgrim.
                queue.pop(0)

            if boarded:
                bus.manifest = boarded
                bus.idle_ticks_at_stop = 0
                self._depart(bus, to_node, from_zone, to_zone)
                events.append({"event": "bus_departed", "unit_id": bus.unit_id, "passenger_count": len(boarded)})
            elif queue:
                # Something is waiting for this corridor, but this bus is
                # already full -- leave it at the stop for the next tick.
                bus.last_action = "AT_STOP_FULL"
            else:
                bus.idle_ticks_at_stop += 1
                bus.last_action = "AT_STOP_WAITING"
                if bus.idle_ticks_at_stop >= self.MAX_IDLE_TICKS_BEFORE_EMPTY_DISPATCH:
                    bus.manifest = []
                    self._depart(bus, to_node, from_zone, to_zone)
                    bus.idle_ticks_at_stop = 0
        return events

    @staticmethod
    def _depart(bus: "BusUnit", to_node: str, from_zone: str, to_zone: str) -> None:
        """Dispatch a bus from its current stop toward the other end of its corridor."""
        bus.status = "in_transit"
        bus.transit_from_node = bus.current_node
        bus.transit_to_node = to_node
        bus.transit_ticks_required = corridor_ticks(from_zone, to_zone)
        bus.transit_ticks_elapsed = 0
        bus.transit_progress = 0.0


@dataclass
class MarshalUnit(OperationalUnit):
    """Patrols a fixed zone and moves to respond when a hazard hits it."""

    patrol_zone: List[str] = field(default_factory=list)
    agents_assisted_count: int = 0

    def step(self, environment_data: dict, pilgrim_snapshots: List[dict]) -> str:
        hazard = environment_data.get("hazard")
        hazard_node = environment_data.get("group_location")
        if hazard and hazard_node in self.patrol_zone:
            if self.current_node != hazard_node:
                self.agents_assisted_count += 1
            self.current_node = hazard_node
            self.target_node = hazard_node
            self.status = "responding"
            self.last_action = f"RESPOND_TO_{hazard_node}"
        else:
            self.status = "patrolling"
            self.last_action = "PATROL"
        return self.last_action

    def to_payload(self) -> dict:
        payload = super().to_payload()
        payload.update({
            "patrol_zone": list(self.patrol_zone),
            "agents_assisted_count": self.agents_assisted_count,
        })
        return payload


@dataclass
class PoliceUnit(OperationalUnit):
    """Patrols checkpoints and switches to crowd-control mode during hazards."""

    patrol_zone: List[str] = field(default_factory=list)
    crowd_control_mode: bool = False

    def step(self, environment_data: dict, pilgrim_snapshots: List[dict]) -> str:
        hazard = environment_data.get("hazard")
        hazard_node = environment_data.get("group_location")
        self.crowd_control_mode = hazard in {"stampede_risk", "crowd_bottleneck"}
        if hazard and hazard_node in self.patrol_zone:
            self.current_node = hazard_node
            self.target_node = hazard_node
            self.status = "crowd_control" if self.crowd_control_mode else "responding"
            self.last_action = f"SECURE_{hazard_node}"
        else:
            self.status = "patrolling"
            self.last_action = "PATROL"
        return self.last_action

    def to_payload(self) -> dict:
        payload = super().to_payload()
        payload.update({
            "patrol_zone": list(self.patrol_zone),
            "crowd_control_mode": self.crowd_control_mode,
        })
        return payload


@dataclass
class AmbulanceUnit(OperationalUnit):
    """Responds to the nearest panicking/high-risk pilgrim, then returns home."""

    home_hospital_node: str = "Field_Hospital"
    responding_to_pilgrim_id: Optional[str] = None
    ticks_since_dispatch: int = 0

    def step(self, environment_data: dict, pilgrim_snapshots: List[dict]) -> str:
        if self.responding_to_pilgrim_id:
            still_urgent = any(
                snapshot["profile"]["pilgrim_id"] == self.responding_to_pilgrim_id
                and _is_urgent(snapshot)
                for snapshot in pilgrim_snapshots
            )
            self.ticks_since_dispatch += 1
            if not still_urgent or self.ticks_since_dispatch >= 4:
                self.responding_to_pilgrim_id = None
                self.ticks_since_dispatch = 0
                self.current_node = self.home_hospital_node
                self.target_node = self.home_hospital_node
                self.status = "returning"
                self.last_action = "RETURN_TO_BASE"
            else:
                self.status = "responding"
                self.last_action = f"ASSIST_{self.responding_to_pilgrim_id}"
            return self.last_action

        urgent_pilgrims = [snapshot for snapshot in pilgrim_snapshots if _is_urgent(snapshot)]
        if urgent_pilgrims:
            target = urgent_pilgrims[0]
            self.responding_to_pilgrim_id = target["profile"]["pilgrim_id"]
            self.ticks_since_dispatch = 0
            self.current_node = target["state"]["current_node"]
            self.target_node = self.current_node
            self.status = "dispatched"
            self.last_action = f"DISPATCH_TO_{self.responding_to_pilgrim_id}"
            return self.last_action

        self.current_node = self.home_hospital_node
        self.target_node = self.home_hospital_node
        self.status = "standby"
        self.last_action = "STANDBY"
        return self.last_action

    def to_payload(self) -> dict:
        payload = super().to_payload()
        payload.update({
            "home_hospital_node": self.home_hospital_node,
            "responding_to_pilgrim_id": self.responding_to_pilgrim_id,
        })
        return payload


class UnitFactory:
    """Spawns the default fixed support-unit fleet used by the dashboard."""

    # Shared corridor fleet -- not owned by any Hamlah. "count" buses are
    # spawned per corridor, split evenly across the two directions so both
    # ends have a bus to board from immediately.
    CORRIDOR_BUS_SPECS: Tuple[dict, ...] = (
        {"stop_a": "Jeddah_Airport", "stop_b": "Masjid_al_Haram_Perimeter",
         "zone_a": "Airport", "zone_b": "Haram", "count": 2},
        {"stop_a": "Makkah_Bus_Station", "stop_b": "Aziziyah_Zone",
         "zone_a": "Haram", "zone_b": "Aziziyah", "count": 1},
        {"stop_a": "Aziziyah_Zone", "stop_b": "Mina_West_Gate",
         "zone_a": "Aziziyah", "zone_b": "Mina", "count": 1},
        {"stop_a": "Mina_Camps_Core", "stop_b": "Arafat_Main_Field",
         "zone_a": "Mina", "zone_b": "Arafat", "count": 2},
        {"stop_a": "Mina_Camps_Core", "stop_b": "Muzdalifah_Open_Area",
         "zone_a": "Mina", "zone_b": "Muzdalifah", "count": 1},
        {"stop_a": "Arafat_Main_Field", "stop_b": "Muzdalifah_Open_Area",
         "zone_a": "Arafat", "zone_b": "Muzdalifah", "count": 1},
    )
    # Cosmetic-only: a non-corridor bus that keeps round 1's local loop
    # behavior, since Jamarat/Mina Camps share one pedestrian zone anyway.
    LEGACY_LOCAL_ROUTE: Tuple[str, ...] = ("Mina_Camps_Core", "Jamarat_Bridge", "Jamarat_Complex")
    MARSHAL_ZONES: Tuple[Tuple[str, ...], ...] = (
        ("Mina_Camps_Core", "Mina_Camp_1", "Mina_Camp_2"),
        ("Arafat_Main_Field", "Arafat_Gate"),
        ("Muzdalifah_Open_Area",),
        ("Jamarat_Complex", "Jamarat_Bridge"),
        ("Mina_Camp_4", "Mina_East_Gate"),
        ("Tawaf_Area", "Sai_Corridor"),
    )
    POLICE_ZONES: Tuple[Tuple[str, ...], ...] = (
        ("Security_Checkpoint_1", "Mina_Camps_Core"),
        ("Jamarat_Complex", "Jamarat_Bridge"),
        ("Masjid_al_Haram_Perimeter", "Makkah_Bus_Station"),
        ("Arafat_Gate", "Arafat_Main_Field"),
    )
    AMBULANCE_HOMES: Tuple[str, ...] = ("Medical_Post_1", "Field_Hospital", "Emergency_Point")

    def spawn_default_fleet(self) -> Dict[str, OperationalUnit]:
        """Build the default fleet: 8 corridor buses + 1 legacy local bus, 6 marshals, 4 police, 3 ambulances."""
        units: Dict[str, OperationalUnit] = {}

        bus_index = 1
        for spec in self.CORRIDOR_BUS_SPECS:
            for slot in range(spec["count"]):
                # Alternate starting stops so a multi-bus corridor has
                # coverage at both ends immediately, not stacked at one end.
                start_at_a = slot % 2 == 0
                unit_id = f"BUS_{bus_index:02d}"
                units[unit_id] = BusUnit(
                    unit_id=unit_id,
                    unit_type="bus",
                    current_node=spec["stop_a"] if start_at_a else spec["stop_b"],
                    target_node=spec["stop_a"] if start_at_a else spec["stop_b"],
                    is_corridor_bus=True,
                    corridor_zone_a=spec["zone_a"],
                    corridor_zone_b=spec["zone_b"],
                    stop_a_node=spec["stop_a"],
                    stop_b_node=spec["stop_b"],
                    status="at_stop",
                )
                bus_index += 1

        units["BUS_LOCAL"] = BusUnit(
            unit_id="BUS_LOCAL",
            unit_type="bus",
            current_node=self.LEGACY_LOCAL_ROUTE[0],
            target_node=self.LEGACY_LOCAL_ROUTE[0],
            is_corridor_bus=False,
            assigned_route=list(self.LEGACY_LOCAL_ROUTE),
        )

        for index, zone in enumerate(self.MARSHAL_ZONES, start=1):
            unit_id = f"MRS_{index:02d}"
            units[unit_id] = MarshalUnit(
                unit_id=unit_id,
                unit_type="marshal",
                current_node=zone[0],
                target_node=zone[0],
                patrol_zone=list(zone),
            )

        for index, zone in enumerate(self.POLICE_ZONES, start=1):
            unit_id = f"POL_{index:02d}"
            units[unit_id] = PoliceUnit(
                unit_id=unit_id,
                unit_type="police",
                current_node=zone[0],
                target_node=zone[0],
                patrol_zone=list(zone),
            )

        for index, home in enumerate(self.AMBULANCE_HOMES, start=1):
            unit_id = f"AMB_{index:02d}"
            units[unit_id] = AmbulanceUnit(
                unit_id=unit_id,
                unit_type="ambulance",
                current_node=home,
                target_node=home,
                home_hospital_node=home,
            )

        return units

    def build_manual_unit(self, unit_type: str, unit_id: str, node_id: str) -> OperationalUnit:
        """Build one manually click-to-place unit (buses excluded -- fixed fleet)."""
        if unit_type == "marshal":
            return MarshalUnit(
                unit_id=unit_id, unit_type="marshal", current_node=node_id, target_node=node_id,
                patrol_zone=[node_id], is_manually_deployed=True,
            )
        if unit_type == "police":
            return PoliceUnit(
                unit_id=unit_id, unit_type="police", current_node=node_id, target_node=node_id,
                patrol_zone=[node_id], is_manually_deployed=True,
            )
        if unit_type == "ambulance":
            return AmbulanceUnit(
                unit_id=unit_id, unit_type="ambulance", current_node=node_id, target_node=node_id,
                home_hospital_node=node_id, is_manually_deployed=True,
            )
        raise ValueError(f"Cannot manually deploy unit_type {unit_type!r} -- buses are a fixed shared fleet")
