"""C5-B3 integration: arrival state, decision ownership and placement."""
import pytest
from mercenary_ambush_reserve import AmbushReserve, ArrivalDecisionOwner, resolve_ambush_arrival_decision
from mercenary_ambush_placement import (
    AmbushTerrainCandidate, PlacementEvidence, PlacementMethod,
    plan_mercenary_ambush_placement,
)
from mercenary_ambush_arrival import (
    AmbushArrivalState, ArrivalStatus, decide_ambush_arrival, as_reserve_state,
)


def plan(legal=True, warband='wb'):
    return plan_mercenary_ambush_placement(
        warband_id=warband, warband_model_count=3, survey_complete=True,
        candidates=(AmbushTerrainCandidate('wood',
            PlacementEvidence.CONFIRMED if legal else PlacementEvidence.REJECTED,
            PlacementEvidence.CONFIRMED, PlacementEvidence.CONFIRMED),),
    )


def arrive(*, placement=None, owner=ArrivalDecisionOwner.CONTROLLING_PLAYER,
           actor=ArrivalDecisionOwner.CONTROLLING_PLAYER, choose=True, turn=2,
           state=None, reserve=None):
    return decide_ambush_arrival(
        state or AmbushArrivalState('wb'), reserve or AmbushReserve('wb'),
        turn=turn, decision_owner=owner, acting_player=actor,
        arrive=choose, placement=placement,
    )


def test_b1_pass_terrain_arrival():
    owner = resolve_ambush_arrival_decision(AmbushReserve('wb'), turn=2,
        end_of_controlling_activation=True, intelligence_target='6+', dice=(3, 3))
    result = arrive(placement=plan(), owner=owner, actor=owner)
    assert result.status is ArrivalStatus.ARRIVED
    assert result.terrain_id == 'wood'


def test_b1_failure_gives_opponent_choice():
    owner = resolve_ambush_arrival_decision(AmbushReserve('wb'), turn=2,
        end_of_controlling_activation=True, intelligence_target='6+', dice=(1, 2))
    assert owner is ArrivalDecisionOwner.OPPOSING_PLAYER
    assert arrive(placement=plan(False), owner=owner, actor=owner).placement_method is PlacementMethod.REINFORCEMENTS


def test_wrong_decider_rejected():
    with pytest.raises(PermissionError):
        arrive(placement=plan(), owner=ArrivalDecisionOwner.OPPOSING_PLAYER)


def test_declining_preserves_reserve():
    assert arrive(choose=False) == AmbushArrivalState('wb')


def test_declining_rejects_placement():
    with pytest.raises(ValueError):
        arrive(placement=plan(), choose=False)


def test_arriving_requires_plan():
    with pytest.raises(ValueError):
        arrive()


def test_turn_one_cannot_arrive():
    with pytest.raises(ValueError):
        arrive(placement=plan(), turn=1)


def test_double_arrival_rejected():
    state = arrive(placement=plan())
    with pytest.raises(ValueError):
        arrive(placement=plan(), state=state)


def test_terrain_arrival_blocks_movement_only_in_arrival_turn():
    state = arrive(placement=plan())
    assert state.may_move(2) is False
    assert state.may_move(3) is None


def test_reinforcements_movement_governed_by_other_rules():
    assert arrive(placement=plan(False)).may_move(2) is None


def test_reserve_cannot_move():
    assert AmbushArrivalState('wb').may_move(3) is False


def test_projection_to_b1_reserve_state():
    state = arrive(placement=plan())
    assert as_reserve_state(state) == AmbushReserve('wb', in_reserve=False, arrived=True)


def test_mismatched_reserve_rejected():
    with pytest.raises(ValueError):
        arrive(placement=plan(), reserve=AmbushReserve('other'))


def test_mismatched_placement_rejected():
    with pytest.raises(ValueError):
        arrive(placement=plan(warband='other'))


def test_arrived_state_requires_method():
    with pytest.raises(ValueError):
        AmbushArrivalState('wb', ArrivalStatus.ARRIVED, 2)


def test_reinforcements_cannot_specify_terrain():
    with pytest.raises(ValueError):
        AmbushArrivalState('wb', ArrivalStatus.ARRIVED, 2, PlacementMethod.REINFORCEMENTS, 'wood')
