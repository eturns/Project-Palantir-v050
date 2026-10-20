"""C5-B3: state transition from B1 arrival choice and B2 placement plan."""
from dataclasses import dataclass
from enum import Enum
from mercenary_ambush_reserve import AmbushReserve, ArrivalDecisionOwner
from mercenary_ambush_placement import AmbushPlacementPlan, PlacementMethod

class ArrivalStatus(Enum):
    RESERVED = 'reserved'
    ARRIVED = 'arrived'

@dataclass(frozen=True)
class AmbushArrivalState:
    warband_id: str
    status: ArrivalStatus = ArrivalStatus.RESERVED
    arrival_turn: int | None = None
    placement_method: PlacementMethod | None = None
    terrain_id: str | None = None

    def __post_init__(self):
        if not isinstance(self.warband_id, str) or not self.warband_id.strip():
            raise ValueError('Warband ID required.')
        if not isinstance(self.status, ArrivalStatus):
            raise TypeError('Invalid arrival status.')
        if self.status is ArrivalStatus.RESERVED:
            if any(x is not None for x in (self.arrival_turn, self.placement_method, self.terrain_id)):
                raise ValueError('Reserved warband cannot have arrival details.')
        else:
            if type(self.arrival_turn) is not int or self.arrival_turn < 2:
                raise ValueError('Arrival turn must be at least two.')
            if not isinstance(self.placement_method, PlacementMethod):
                raise ValueError('Arrival method required.')
            if self.placement_method is PlacementMethod.TERRAIN:
                if not isinstance(self.terrain_id, str) or not self.terrain_id.strip():
                    raise ValueError('Terrain arrival needs terrain ID.')
            elif self.terrain_id is not None:
                raise ValueError('Reinforcements cannot specify terrain ID.')

    def may_move(self, turn: int) -> bool | None:
        """False means prohibited; None delegates to ordinary movement rules.

        In particular, reinforcements are NOT automatically granted movement.
        """
        if type(turn) is not int or turn < 1:
            raise ValueError('Turn must be positive.')
        if self.status is ArrivalStatus.RESERVED:
            return False
        if self.placement_method is PlacementMethod.TERRAIN and turn == self.arrival_turn:
            return False
        return None


def decide_ambush_arrival(
    state: AmbushArrivalState,
    reserve: AmbushReserve,
    *,
    turn: int,
    decision_owner: ArrivalDecisionOwner,
    acting_player: ArrivalDecisionOwner,
    arrive: bool,
    placement: AmbushPlacementPlan | None = None,
) -> AmbushArrivalState:
    """Apply decision from B1 and placement planned by B2; no geometry inferred.

    The caller is responsible for supplying the B1 decision owner from this
    specific turn and a B2-verified placement plan, not a fabricated plan.
    """
    if not isinstance(state, AmbushArrivalState) or not isinstance(reserve, AmbushReserve):
        raise TypeError('Invalid reserve or arrival state.')
    if state.warband_id != reserve.warband_id:
        raise ValueError('Warband ID mismatch.')
    if state.status is not ArrivalStatus.RESERVED or not reserve.in_reserve or reserve.arrived:
        raise ValueError('Warband is not currently awaiting arrival.')
    if type(turn) is not int or turn < 2:
        raise ValueError('Ambush arrival starts on turn two.')
    if not isinstance(decision_owner, ArrivalDecisionOwner):
        raise TypeError('Decision owner must be the B1 result.')
    if acting_player is not decision_owner:
        raise PermissionError('This player cannot choose the arrival.')
    if type(arrive) is not bool:
        raise TypeError('Arrival choice must be bool.')
    if not arrive:
        if placement is not None:
            raise ValueError('Do not supply placement when declining arrival.')
        return state
    if not isinstance(placement, AmbushPlacementPlan) or placement.warband_id != state.warband_id:
        raise ValueError('Matching B2 placement plan required.')
    return AmbushArrivalState(
        warband_id=state.warband_id, status=ArrivalStatus.ARRIVED,
        arrival_turn=turn, placement_method=placement.method,
        terrain_id=placement.terrain_id,
    )


def as_reserve_state(state: AmbushArrivalState) -> AmbushReserve:
    if not isinstance(state, AmbushArrivalState):
        raise TypeError('Expected AmbushArrivalState.')
    arrived = state.status is ArrivalStatus.ARRIVED
    return AmbushReserve(state.warband_id, in_reserve=not arrived, arrived=arrived)
