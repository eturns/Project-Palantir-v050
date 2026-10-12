import pytest
from reposition_mechanics import (
    RepositionKind, RepositionRequest, RepositionRule,
    RepositionTiming, RepositionUsage, apply_reposition,
    validate_reposition, unnatural_speed_rule, spiritual_displacement_rule,
)


def request(actor="shadow", destination=(3.0, 0.0), **kwargs):
    return RepositionRequest(
        actor_id=actor, origin=(0.0, 0.0), destination=destination,
        timing=RepositionTiming.PRE_HEROIC_ACTIONS, **kwargs,
    )


def turn():
    u = RepositionUsage()
    u.begin_turn(1)
    return u


def test_unnatural_speed_exactly_three_inches():
    assert validate_reposition(unnatural_speed_rule("shadow"), request(), turn())[0]


def test_unnatural_speed_beyond_three_inches_rejected():
    assert not validate_reposition(unnatural_speed_rule("shadow"), request(destination=(3.001, 0.0)), turn())[0]


def test_placement_cannot_be_enemy_base_contact():
    assert not validate_reposition(unnatural_speed_rule("shadow"), request(in_enemy_base_contact=True), turn())[0]


def test_placement_legality_is_caller_supplied_and_checked():
    assert not validate_reposition(unnatural_speed_rule("shadow"), request(legal_placement=False), turn())[0]


def test_wrong_timing_rejected():
    r = RepositionRequest("shadow", (0.0, 0.0), (1.0, 0.0), RepositionTiming.OTHER)
    assert not validate_reposition(unnatural_speed_rule("shadow"), r, turn())[0]


def test_self_reposition_spends_its_once_per_turn_usage():
    u = turn()
    rule = unnatural_speed_rule("shadow")
    apply_reposition(rule, request(), u)
    assert not validate_reposition(rule, request(), u)[0]
    u.begin_turn(2)
    assert validate_reposition(rule, request(), u)[0]


def test_spiritual_displacement_requires_second_eligible_knight():
    rule = spiritual_displacement_rule()
    assert not validate_reposition(rule, request(actor="knight1"), turn())[0]
    good = request(actor="knight1", destination=(21.0, 0.0), anchor_id="knight2", anchor_position=(20.0, 0.0), anchor_is_eligible=True)
    assert validate_reposition(rule, good, turn())[0]


def test_spiritual_displacement_measures_from_anchor_not_actor():
    r = request(actor="knight1", destination=(4.0, 0.0), anchor_id="knight2", anchor_position=(20.0, 0.0), anchor_is_eligible=True)
    assert not validate_reposition(spiritual_displacement_rule(), r, turn())[0]


def test_spiritual_displacement_is_shared_once_per_turn_between_pair():
    u = turn()
    rule = spiritual_displacement_rule()
    first = request(actor="knight1", destination=(21.0, 0.0), anchor_id="knight2", anchor_position=(20.0, 0.0), anchor_is_eligible=True)
    second = request(actor="knight2", destination=(1.0, 0.0), anchor_id="knight1", anchor_position=(0.0, 0.0), anchor_is_eligible=True)
    apply_reposition(rule, first, u)
    assert not validate_reposition(rule, second, u)[0]
    u.begin_turn(2)
    assert validate_reposition(rule, second, u)[0]


def test_reposition_does_not_count_as_moving():
    assert unnatural_speed_rule("s").does_not_count_as_moving
    assert spiritual_displacement_rule().does_not_count_as_moving


def test_missing_anchor_or_actor_is_rejected():
    r = request(actor="knight1", anchor_id="knight2", anchor_position=(1.0, 0.0), anchor_is_eligible=True, anchor_on_board=False)
    assert not validate_reposition(spiritual_displacement_rule(), r, turn())[0]
    assert not validate_reposition(unnatural_speed_rule("shadow"), request(actor_on_board=False), turn())[0]


def test_invalid_position_cannot_be_used():
    assert not validate_reposition(unnatural_speed_rule("shadow"), request(destination=(float("nan"), 0.0)), turn())[0]
