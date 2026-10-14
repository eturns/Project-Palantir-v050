"""DEV-077S-I2-H3-B: conditional objective reachability diagnostics."""
from fractions import Fraction
import pytest
from objective_reachability import (
    ObjectiveTravelEvidence, ReachabilityCheck,
    assess_objective_reachability,
)

T = ReachabilityCheck.VERIFIED_TRUE
F = ReachabilityCheck.VERIFIED_FALSE
U = ReachabilityCheck.UNKNOWN

def make(**overrides):
    data = dict(model_id="DG_NEC#1", objective_id="CENTRE",
                distance_inches=Fraction(12), turns_available=2,
                movement_inches_per_turn=Fraction(6), route_legal=T,
                placement_legal=T, terrain_route_verified=T)
    data.update(overrides)
    return ObjectiveTravelEvidence(**data)

def test_exactly_reachable_boundary():
    result = assess_objective_reachability(make())
    assert result.status == "conditionally_reachable"
    assert result.minimum_turns_at_declared_speed == 2

def test_reachability_is_not_occupation_or_scoring():
    result = assess_objective_reachability(make())
    assert result.occupation_verified is None and result.control_verified is None
    assert result.victory_points is None and result.dashboard_score is None

def test_not_enough_turns():
    result = assess_objective_reachability(make(turns_available=1))
    assert result.status == "beyond_declared_turn_ceiling"
    assert result.maximum_travel_inches == 6

def test_fractional_speed_preserves_exact_arithmetic():
    result = assess_objective_reachability(make(
        distance_inches=Fraction(5, 2),
        turns_available=2, movement_inches_per_turn=Fraction(3, 2)))
    assert result.minimum_turns_at_declared_speed == 2
    assert result.maximum_travel_inches == 3

@pytest.mark.parametrize("field", ["route_legal","placement_legal","terrain_route_verified","movement_available"])
def test_unverified_constraint_remains_unresolved(field):
    result = assess_objective_reachability(make(**{field: U}))
    assert result.status == "unresolved"

@pytest.mark.parametrize("field", ["route_legal","placement_legal","terrain_route_verified","movement_available"])
def test_verified_obstruction_blocks(field):
    result = assess_objective_reachability(make(**{field: F}))
    assert result.status == "blocked"

def test_blocked_outweighs_unknown():
    assert assess_objective_reachability(make(route_legal=F,placement_legal=U)).status == "blocked"

def test_unknown_can_not_be_proven_from_distance():
    assert assess_objective_reachability(make(distance_inches=50,route_legal=U)).status == "unresolved"

def test_at_objective_does_not_imply_control():
    result = assess_objective_reachability(make(distance_inches=0,turns_available=0))
    assert result.status == "conditionally_reachable"
    assert result.minimum_turns_at_declared_speed == 0
    assert result.control_verified is None

def test_no_movement_cannot_reach_nonzero_distance():
    result = assess_objective_reachability(make(movement_inches_per_turn=0))
    assert result.minimum_turns_at_declared_speed is None
    assert result.status == "beyond_declared_turn_ceiling"

@pytest.mark.parametrize("field,value", [
    ("distance_inches",-1),("movement_inches_per_turn",-1),
    ("distance_inches",0.5),("turns_available",True),("turns_available",-1)])
def test_invalid_geometry_rejected(field,value):
    with pytest.raises(ValueError):
        make(**{field:value})

def test_incorrect_check_type_rejected():
    with pytest.raises(TypeError):
        make(route_legal=True)
