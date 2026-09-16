"""Hamlah (Hajj campaign) and support-unit models for HajjSim.

A Hamlah groups pilgrim agents under a single campaign operator and carries
the staggered dispatch offset used by the time engine in ``hajj_agents.py``.
Support units (buses, marshals, police, ambulances) are lightweight reactive
agents defined separately from the four-layer ``PilgrimAgent`` model, since
they don't need memory or a behavior engine -- just simple per-tick rules.
"""

import json
import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# One-way dependency only (hajj_agents.py never imports this module), so this
# stays acyclic.
from hajj_agents import corridor_minutes, corridor_ticks, next_hop_zone, zone_of

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


# ============================================================
# Bus routing: constants, route model, and the route registry
# ------------------------------------------------------------
# A bus is demand-driven and route-bound. It only moves when it is carrying
# enough riders to be worth dispatching, it never exceeds its capacity, and
# every hop it makes must be an adjacent pair of stops on its own route that
# also corresponds to a real corridor in the road network.
# ============================================================

# --- Tunables (change these, not the logic) -----------------------------
# A bus stays put until it is carrying at least this many riders.
MIN_RIDERS_TO_MOVE = 5
# Default seats per bus. Boarding never exceeds this.
DEFAULT_BUS_CAPACITY = 40

# A bus with fewer than MIN_RIDERS_TO_MOVE will still run if it has been
# waiting this long AND has at least one rider, so a handful of pilgrims on a
# quiet corridor are not stranded forever. Set to 0 to disable and enforce the
# minimum absolutely.
MAX_WAIT_TICKS_BEFORE_UNDERFULL_DISPATCH = 6

# An EMPTY bus may reposition to the other end of its own route only when
# riders are waiting there and no other bus on that route can serve them.
# This is the deadlock guard: without it, once every bus on a corridor ends up
# at the same end, pilgrims at the far end wait forever. It is still
# demand-driven (it only happens when there is real demand it can reach) and
# still route-bound (it can only move along its own route). Set to False to
# forbid all empty movement.
ALLOW_EMPTY_REPOSITIONING = True

# Canonical boarding stop for each inter-city corridor, as (zone_a, zone_b) ->
# (stop_in_zone_a, stop_in_zone_b). This is the single source of truth for
# where a bus may legally stop, and is what new routes are built from.
CORRIDOR_STOPS: Dict[Tuple[str, str], Tuple[str, str]] = {
    ("Airport", "Haram"): ("Jeddah_Airport", "Masjid_al_Haram_Perimeter"),
    ("Haram", "Aziziyah"): ("Makkah_Bus_Station", "Aziziyah_Zone"),
    ("Aziziyah", "Mina"): ("Aziziyah_Zone", "Mina_West_Gate"),
    ("Mina", "Arafat"): ("Mina_Camps_Core", "Arafat_Main_Field"),
    ("Mina", "Muzdalifah"): ("Mina_Camps_Core", "Muzdalifah_Open_Area"),
    ("Arafat", "Muzdalifah"): ("Arafat_Main_Field", "Muzdalifah_Open_Area"),
}

# Bus decisions are logged line-by-line for traceability. Set BUS_LOG=0 to
# silence it -- a 240-tick run with a full fleet is a lot of output.
BUS_LOG_ENABLED = (os.environ.get("BUS_LOG") or "1").strip().lower() not in {"0", "false", "no", "off"}


def bus_log(message: str) -> None:
    """Emit one bus-behaviour line, unless logging has been switched off."""
    if BUS_LOG_ENABLED:
        print(message)


def corridor_stops_for(zone_a: str, zone_b: str) -> Optional[Tuple[str, str]]:
    """Return the (stop_in_zone_a, stop_in_zone_b) pair for a corridor.

    Handles either ordering, and returns None when no such corridor exists --
    which is what makes an invalid route segment impossible to build.
    """
    direct = CORRIDOR_STOPS.get((zone_a, zone_b))
    if direct:
        return direct
    reverse = CORRIDOR_STOPS.get((zone_b, zone_a))
    if reverse:
        return reverse[1], reverse[0]
    return None


def is_real_corridor(zone_a: str, zone_b: str) -> bool:
    """True when two zones are directly connected in the road network."""
    return corridor_minutes(zone_a, zone_b) is not None and corridor_stops_for(zone_a, zone_b) is not None


def plan_zone_path(from_zone: str, to_zone: str) -> List[str]:
    """Shortest sequence of zones from one to another over real corridors.

    Walks ``next_hop_zone`` (the same BFS the pilgrims use), so a generated
    route can only ever be made of segments that genuinely exist.
    """
    if from_zone == to_zone:
        return []
    path = [from_zone]
    guard = 0
    current = from_zone
    while current != to_zone and guard < 12:
        guard += 1
        hop = next_hop_zone(current, to_zone)
        if hop is None:
            return []
        path.append(hop)
        current = hop
    return path if current == to_zone else []


@dataclass
class BusRoute:
    """An ordered list of stops a bus is allowed to travel between.

    ``stops`` and ``zones`` are parallel lists: ``stops[i]`` is the boarding
    node in ``zones[i]``. A bus walks this list one index at a time and
    reverses at either end, so it can never appear anywhere that is not one of
    its own stops.
    """

    route_id: str
    stops: List[str] = field(default_factory=list)
    zones: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.stops) != len(self.zones):
            raise ValueError(f"Route {self.route_id}: stops and zones must be the same length")
        if len(self.stops) < 2:
            raise ValueError(f"Route {self.route_id}: a route needs at least two stops")

    @property
    def zone_pairs(self) -> List[Tuple[str, str]]:
        """Every consecutive zone pair the route claims to connect."""
        return list(zip(self.zones, self.zones[1:]))

    def is_valid(self) -> bool:
        """True only when every segment is a real corridor in the road network."""
        return all(is_real_corridor(a, b) for a, b in self.zone_pairs)

    def serves(self, from_zone: str, to_zone: str) -> bool:
        """True when this route connects two zones as an adjacent segment."""
        return (from_zone, to_zone) in self.zone_pairs or (to_zone, from_zone) in self.zone_pairs

    def describe(self) -> str:
        """Human-readable 'Stop A -> Stop B -> Stop C' form for logs."""
        return " -> ".join(self.stops)

    def to_payload(self) -> dict:
        """JSON-safe form for the dashboard."""
        return {"route_id": self.route_id, "stops": list(self.stops), "zones": list(self.zones)}


class BusRouteRegistry:
    """Every route the fleet serves, plus creation of new ones when needed.

    New routes are a last resort: demand is only ever routed onto a freshly
    built route when no existing route already covers it.
    """

    def __init__(self):
        self.routes: Dict[str, BusRoute] = {}
        self._created_count = 0

    def register(self, route: BusRoute) -> BusRoute:
        """Add a route, refusing any that is not valid in the road network."""
        if not route.is_valid():
            raise ValueError(f"Route {route.route_id} has a segment that is not a real corridor: {route.describe()}")
        self.routes[route.route_id] = route
        return route

    def reset(self) -> None:
        """Forget every route (used when the fleet is respawned)."""
        self.routes.clear()
        self._created_count = 0

    def find_route_serving(self, from_zone: str, to_zone: str) -> Optional[BusRoute]:
        """Return an existing route that already covers this corridor, if any."""
        for route in self.routes.values():
            if route.serves(from_zone, to_zone):
                return route
        return None

    def create_route_for(self, from_zone: str, to_zone: str) -> Optional[BusRoute]:
        """Build and register a new route for unmet demand, or None if impossible.

        Every segment is taken from the corridor graph, so a generated route is
        valid by construction; it is validated again on registration.
        """
        zone_path = plan_zone_path(from_zone, to_zone)
        if len(zone_path) < 2:
            return None

        stops: List[str] = []
        for index, (zone_a, zone_b) in enumerate(zip(zone_path, zone_path[1:])):
            pair = corridor_stops_for(zone_a, zone_b)
            if pair is None:
                # A segment with no real corridor -- refuse the whole route
                # rather than inventing a road.
                return None
            if index == 0:
                stops.append(pair[0])
            stops.append(pair[1])

        self._created_count += 1
        route = BusRoute(route_id=f"ROUTE_GEN_{self._created_count:02d}", stops=stops, zones=list(zone_path))
        try:
            return self.register(route)
        except ValueError:
            self._created_count -= 1
            return None

    def to_payload(self) -> List[dict]:
        """JSON-safe list of all known routes."""
        return [route.to_payload() for route in self.routes.values()]


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

    passenger_capacity: int = DEFAULT_BUS_CAPACITY
    is_corridor_bus: bool = True

    # -- Demand-driven movement --
    # The bus will not depart with fewer riders than this (see MIN_RIDERS_TO_MOVE).
    min_riders_to_move: int = MIN_RIDERS_TO_MOVE
    # How many consecutive ticks it has been holding for more riders.
    waiting_ticks: int = 0

    # -- Route (ordered stops the bus is allowed to travel between) --
    route_id: str = ""
    route_stops: List[str] = field(default_factory=list)
    route_zones: List[str] = field(default_factory=list)
    route_index: int = 0

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

    # ------------------------------------------------------------------
    # Riders and capacity
    # ------------------------------------------------------------------
    @property
    def current_riders(self) -> int:
        """How many pilgrims are on board right now."""
        return len(self.manifest)

    @property
    def remaining_capacity(self) -> int:
        """Free seats. Never negative, even if data were somehow inconsistent."""
        return max(0, self.passenger_capacity - self.current_riders)

    @property
    def is_full(self) -> bool:
        """True when no further rider can be accepted."""
        return self.remaining_capacity <= 0

    def has_minimum_riders(self) -> bool:
        """True when the bus is carrying enough riders to be worth dispatching."""
        return self.current_riders >= self.min_riders_to_move

    # ------------------------------------------------------------------
    # Route
    # ------------------------------------------------------------------
    def current_zone(self) -> str:
        """The zone of the stop the bus is currently at."""
        if self.route_zones and 0 <= self.route_index < len(self.route_zones):
            return self.route_zones[self.route_index]
        return zone_of(self.current_node)

    def next_route_index(self) -> Optional[int]:
        """Index of the next stop, reversing at either end of the route.

        Returns None only for a degenerate route with fewer than two stops,
        which means the bus has nowhere legal to go.
        """
        if len(self.route_stops) < 2:
            return None
        if self.direction_forward:
            if self.route_index + 1 < len(self.route_stops):
                return self.route_index + 1
            # End of the line: turn around (Stop D -> Stop C -> ... -> Stop A).
            self.direction_forward = False
            return self.route_index - 1
        if self.route_index - 1 >= 0:
            return self.route_index - 1
        self.direction_forward = True
        return self.route_index + 1

    def peek_next_stop(self) -> Optional[Tuple[int, str, str]]:
        """Look at the next (index, stop_node, zone) WITHOUT flipping direction.

        next_route_index() mutates direction_forward when it turns around, so
        anything that only wants to *ask* where the bus would go next -- a
        capacity check, a log line, a demand lookup -- must use this instead.
        """
        if len(self.route_stops) < 2:
            return None
        forward = self.direction_forward
        index = self.route_index + 1 if forward else self.route_index - 1
        if index >= len(self.route_stops):
            index = self.route_index - 1
        elif index < 0:
            index = self.route_index + 1
        if not 0 <= index < len(self.route_stops):
            return None
        return index, self.route_stops[index], self.route_zones[index]

    def is_valid_next_hop(self, to_node: str) -> bool:
        """True only if to_node is an ADJACENT stop on this bus's own route.

        This is the guard that makes shortcuts, teleports and jumps onto an
        unrelated route impossible: a destination that is not the immediate
        neighbour of the current position in route_stops is refused, and so is
        one whose zone pair is not a real corridor.
        """
        if to_node not in self.route_stops:
            return False
        neighbours = []
        if self.route_index - 1 >= 0:
            neighbours.append(self.route_index - 1)
        if self.route_index + 1 < len(self.route_stops):
            neighbours.append(self.route_index + 1)
        for index in neighbours:
            if self.route_stops[index] == to_node:
                return is_real_corridor(self.route_zones[self.route_index], self.route_zones[index])
        return False

    def route_description(self) -> str:
        """'Stop A -> Stop B -> Stop C' for logging."""
        return " -> ".join(self.route_stops) if self.route_stops else "(no route)"

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
            "current_riders": self.current_riders,
            "remaining_capacity": self.remaining_capacity,
            "min_riders_to_move": self.min_riders_to_move,
            "waiting_ticks": self.waiting_ticks,
            "route_id": self.route_id,
            "route_stops": list(self.route_stops),
            "route_zones": list(self.route_zones),
            "route_index": self.route_index,
            "direction_forward": self.direction_forward,
        })
        return payload


class ConvoyDispatchCoordinator:
    """Owns all real corridor-bus movement: arrival/disembark, then dispatch.

    Runs once per tick, after pilgrims have decided their own actions (so it
    sees freshly-set AWAITING_TRANSPORT states) and before marshal/police/
    ambulance stepping (so, e.g., an ambulance doesn't try to reach a pilgrim
    who just boarded a bus this same tick).

    Every bus is evaluated in this fixed order:

        1. current passenger count
        2. bus capacity
        3. a valid route exists
        4. passenger destinations / demand
        5. use an existing route if possible
        6. create a new route only if necessary
        7. move only along a valid route segment
    """

    def __init__(self, route_registry: Optional["BusRouteRegistry"] = None):
        self.routes = route_registry or BusRouteRegistry()
        # Corridors we have already tried and failed to build a route for, so
        # the planner does not retry (and re-log) the same impossible demand
        # on every single tick.
        self._unservable: set = set()

    def reset(self) -> None:
        """Clear planner state (called when the fleet is respawned)."""
        self.routes.reset()
        self._unservable.clear()

    def step(self, agents: Dict[str, object], units: Dict[str, "OperationalUnit"], tick: int) -> List[dict]:
        """Advance every corridor bus one tick; returns a list of event dicts."""
        buses = [unit for unit in units.values() if isinstance(unit, BusUnit) and unit.is_corridor_bus]
        self._sync_routes(buses)
        events = self._advance_transit_and_disembark(agents, buses)
        demand = self._collect_demand(agents)
        events += self._dispatch_from_stops(agents, buses, demand)
        events += self._plan_routes_for_unmet_demand(demand, buses, units)
        return events

    def _sync_routes(self, buses: List["BusUnit"]) -> None:
        """Make sure every bus's own route is registered and valid."""
        for bus in buses:
            if not bus.route_stops or bus.route_id in self.routes.routes:
                continue
            try:
                self.routes.register(BusRoute(
                    route_id=bus.route_id or f"ROUTE_{bus.unit_id}",
                    stops=list(bus.route_stops),
                    zones=list(bus.route_zones),
                ))
            except ValueError as error:
                bus_log(f"{bus.unit_id}: refusing an invalid route -- {error}")

    # ------------------------------------------------------------------
    # Arrival
    # ------------------------------------------------------------------
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
            bus.idle_ticks_at_stop = 0
            bus.waiting_ticks = 0
            bus.last_action = f"ARRIVED_AT_{arrival_node}"
            riders = len(bus.manifest)
            for pilgrim_id in bus.manifest:
                agent = agents.get(pilgrim_id)
                if agent is None:
                    continue
                agent.state.current_node = arrival_node
                agent.state.travel_state = "PEDESTRIAN"
                agent.state.boarded_unit_id = None
            if riders:
                bus_log(f"{bus.unit_id}: arrived at {arrival_node}, {riders} rider(s) disembarked")
            events.append({
                "event": "bus_arrived", "unit_id": bus.unit_id,
                "node": arrival_node, "passenger_count": riders,
            })
            bus.manifest = []
        return events

    # ------------------------------------------------------------------
    # Demand
    # ------------------------------------------------------------------
    @staticmethod
    def _collect_demand(agents: Dict[str, object]) -> Dict[Tuple[str, str], List[object]]:
        """Group queued pilgrims by the single corridor hop each one needs next.

        Oldest-first within each Hamlah, so cohorts board together and nobody
        starves (FIFO).
        """
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
        return waiting_by_corridor

    # ------------------------------------------------------------------
    # Boarding and dispatch
    # ------------------------------------------------------------------
    def _dispatch_from_stops(
        self,
        agents: Dict[str, object],
        buses: List["BusUnit"],
        demand: Dict[Tuple[str, str], List[object]],
    ) -> List[dict]:
        events: List[dict] = []

        for bus in buses:
            if bus.status != "at_stop":
                continue

            # (3) A valid route must exist before anything else is considered.
            next_hop = bus.peek_next_stop()
            if next_hop is None:
                bus.last_action = "NO_ROUTE"
                bus_log(f"{bus.unit_id}: no valid route assigned -- staying stationary")
                continue
            _, to_node, to_zone = next_hop
            from_zone = bus.current_zone()

            # (4) Demand for the direction this bus is facing.
            queue = demand.get((from_zone, to_zone), [])

            # (2) Capacity: board up to, and never beyond, the free seats.
            boarded: List[str] = []
            while queue and not bus.is_full:
                agent = queue[0]
                agent.state.travel_state = "IN_TRANSIT"
                agent.state.boarded_unit_id = bus.unit_id
                bus.manifest.append(agent.profile.pilgrim_id)
                boarded.append(agent.profile.pilgrim_id)
                # Pop from the shared queue so a second bus on this corridor
                # this same tick doesn't double-board the same pilgrim.
                queue.pop(0)

            if queue and bus.is_full:
                bus_log(
                    f"{bus.unit_id}: {bus.current_riders}/{bus.passenger_capacity} capacity reached -- "
                    f"{len(queue)} pilgrim(s) left waiting at {bus.current_node}"
                )

            # (1) Passenger count decides whether it is allowed to move at all.
            if bus.has_minimum_riders():
                bus_log(
                    f"{bus.unit_id}: {bus.current_riders} riders -> minimum reached, starting route "
                    f"({bus.current_node} -> {to_node})"
                )
                self._depart(bus, events)
                continue

            # Under the minimum: hold. This is the core rule -- an under-filled
            # bus stays where it is.
            bus.waiting_ticks += 1
            bus.idle_ticks_at_stop += 1

            if bus.current_riders > 0:
                bus.status = "at_stop"
                bus.last_action = "HOLDING_FOR_RIDERS"
                bus_log(
                    f"{bus.unit_id}: {bus.current_riders} riders -> staying stationary "
                    f"(minimum = {bus.min_riders_to_move}), waited {bus.waiting_ticks} tick(s)"
                )
                # Escape hatch so a handful of pilgrims on a quiet corridor are
                # not stranded for the rest of the run.
                if (
                    MAX_WAIT_TICKS_BEFORE_UNDERFULL_DISPATCH > 0
                    and bus.waiting_ticks >= MAX_WAIT_TICKS_BEFORE_UNDERFULL_DISPATCH
                ):
                    bus_log(
                        f"{bus.unit_id}: held {bus.waiting_ticks} tick(s) with {bus.current_riders} rider(s) "
                        f"-> dispatching under-full so they are not stranded"
                    )
                    self._depart(bus, events)
                continue

            # Completely empty.
            bus.last_action = "AT_STOP_EMPTY"
            bus_log(f"{bus.unit_id}: 0 riders -> staying stationary (minimum = {bus.min_riders_to_move})")
            if ALLOW_EMPTY_REPOSITIONING and self._should_reposition(bus, buses, demand, to_zone):
                bus_log(
                    f"{bus.unit_id}: riders waiting at {to_node} with no bus there -> "
                    f"repositioning empty along its own route"
                )
                self._depart(bus, events)
        return events

    @staticmethod
    def _should_reposition(
        bus: "BusUnit",
        buses: List["BusUnit"],
        demand: Dict[Tuple[str, str], List[object]],
        to_zone: str,
    ) -> bool:
        """True when an empty bus should move to reach demand it alone can serve.

        Strictly limited: there must be real demand at the far end of this
        bus's own route, and no other bus already positioned to serve it.
        """
        return_zone = bus.current_zone()
        onward = demand.get((to_zone, return_zone), [])
        if not onward:
            return False
        for other in buses:
            if other is bus:
                continue
            # Only a bus that serves THIS corridor counts as coverage. A bus
            # parked in the same zone on an unrelated route cannot pick these
            # pilgrims up, so treating it as coverage would strand them --
            # which is exactly what happened before this check was narrowed.
            other_pairs = list(zip(other.route_zones, other.route_zones[1:]))
            if (to_zone, return_zone) not in other_pairs and (return_zone, to_zone) not in other_pairs:
                continue
            if other.status == "at_stop" and other.current_zone() == to_zone:
                return False  # someone who can serve them is already there
            if other.status == "in_transit" and zone_of(other.transit_to_node) == to_zone:
                return False  # someone who can serve them is already on the way
        return True

    def _depart(self, bus: "BusUnit", events: List[dict]) -> None:
        """Move a bus one segment along its own route, validating the hop first."""
        next_hop = bus.peek_next_stop()
        if next_hop is None:
            bus.last_action = "NO_ROUTE"
            return
        index, to_node, to_zone = next_hop

        # (7) The hop must be an adjacent stop on this route AND a real
        # corridor. A bus that somehow asked for anything else stays put.
        if not bus.is_valid_next_hop(to_node):
            bus.last_action = "INVALID_SEGMENT_REFUSED"
            bus_log(
                f"{bus.unit_id}: REFUSED move {bus.current_node} -> {to_node} "
                f"-- not an adjacent segment of its route ({bus.route_description()})"
            )
            return

        from_zone = bus.route_zones[bus.route_index]
        from_node = bus.current_node
        bus.status = "in_transit"
        bus.transit_from_node = from_node
        bus.transit_to_node = to_node
        bus.transit_ticks_required = corridor_ticks(from_zone, to_zone)
        bus.transit_ticks_elapsed = 0
        bus.transit_progress = 0.0
        bus.target_node = to_node
        bus.idle_ticks_at_stop = 0
        bus.waiting_ticks = 0
        bus.last_action = f"DEPARTED_FOR_{to_node}"

        # Advance the route cursor, flipping direction at either end.
        bus.next_route_index()
        bus.route_index = index

        bus_log(
            f"{bus.unit_id}: moving {from_node} -> {to_node} "
            f"({bus.current_riders}/{bus.passenger_capacity} capacity, {bus.transit_ticks_required} tick(s))"
        )
        events.append({
            "event": "bus_departed", "unit_id": bus.unit_id,
            "from_node": from_node, "to_node": to_node,
            "passenger_count": bus.current_riders,
        })

    # ------------------------------------------------------------------
    # Route creation (last resort)
    # ------------------------------------------------------------------
    def _plan_routes_for_unmet_demand(
        self,
        demand: Dict[Tuple[str, str], List[object]],
        buses: List["BusUnit"],
        units: Dict[str, "OperationalUnit"],
    ) -> List[dict]:
        """Create a route only for demand no existing route can serve.

        (5) existing routes first, (6) a new route only if genuinely needed.
        """
        events: List[dict] = []
        for (from_zone, to_zone), waiting in demand.items():
            if not waiting or (from_zone, to_zone) in self._unservable:
                continue

            # (5) Does any bus already serve this corridor? Then nothing to do.
            already_served = False
            for bus in buses:
                if len(bus.route_zones) < 2:
                    continue
                pairs = list(zip(bus.route_zones, bus.route_zones[1:]))
                if (from_zone, to_zone) in pairs or (to_zone, from_zone) in pairs:
                    already_served = True
                    break
            if already_served:
                continue

            bus_log(
                f"Dispatcher: {len(waiting)} pilgrim(s) need {from_zone} -> {to_zone}, "
                f"no bus serves it -- checking existing routes"
            )
            existing = self.routes.find_route_serving(from_zone, to_zone)
            if existing is not None:
                bus_log(f"Dispatcher: existing route {existing.route_id} covers it ({existing.describe()})")
                new_route = existing
            else:
                bus_log(f"Dispatcher: no suitable route -> creating a new valid route for {from_zone} -> {to_zone}")
                new_route = self.routes.create_route_for(from_zone, to_zone)
                if new_route is None:
                    bus_log(f"Dispatcher: {from_zone} -> {to_zone} is not reachable over the road network -- skipping")
                    self._unservable.add((from_zone, to_zone))
                    continue
                bus_log(f"Dispatcher: created {new_route.route_id}: {new_route.describe()}")

            # (6) Put exactly one bus on it -- no more than the demand needs.
            unit_id = f"BUS_{new_route.route_id}"
            if unit_id in units:
                continue
            start_index = new_route.zones.index(from_zone) if from_zone in new_route.zones else 0
            units[unit_id] = BusUnit(
                unit_id=unit_id,
                unit_type="bus",
                current_node=new_route.stops[start_index],
                target_node=new_route.stops[start_index],
                is_corridor_bus=True,
                corridor_zone_a=new_route.zones[0],
                corridor_zone_b=new_route.zones[-1],
                stop_a_node=new_route.stops[0],
                stop_b_node=new_route.stops[-1],
                route_id=new_route.route_id,
                route_stops=list(new_route.stops),
                route_zones=list(new_route.zones),
                route_index=start_index,
                status="at_stop",
            )
            bus_log(f"Dispatcher: assigned {unit_id} to {new_route.route_id}")
            events.append({
                "event": "route_created", "route_id": new_route.route_id,
                "unit_id": unit_id, "stops": list(new_route.stops),
            })
        return events


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
                # The corridor IS the route: an ordered two-stop list the bus
                # walks back and forth. route_index says which end it is at,
                # and direction_forward which way it is facing, so its very
                # first departure heads for the opposite stop.
                route_stops = [spec["stop_a"], spec["stop_b"]]
                route_zones = [spec["zone_a"], spec["zone_b"]]
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
                    route_id=f"ROUTE_{spec['zone_a']}_{spec['zone_b']}",
                    route_stops=route_stops,
                    route_zones=route_zones,
                    route_index=0 if start_at_a else 1,
                    direction_forward=start_at_a,
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
