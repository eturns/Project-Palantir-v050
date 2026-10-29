"""DEV-077-SMAUG-C3B/E focussed tests."""
from fractions import Fraction
import pytest
from defensive_state import DefensiveState
from smaug_missing_scale import calculate_missing_scale_evidence
from smaug_missing_scale_volley import IncomingMissile, calculate_smaug_missing_scale_volley


def get(*shooters, wounds=20, fate=0):
    return calculate_smaug_missing_scale_volley(
        target_profile_id="SMAUG", shooters=tuple(shooters),
        state=DefensiveState(wounds, fate))


def test_one_shot_matches_original_missing_scale():
    shot = IncomingMissile("a", "4+", 3)
    actual = get(shot)
    single = calculate_missing_scale_evidence(
        shooter_shoot_value="4+", missile_strength=3)
    assert actual.incoming_wound_distribution[0] == single.miss_or_no_wound_probability
    assert actual.incoming_wound_distribution[1] == single.ordinary_wound_probability
    assert actual.incoming_wound_distribution[3] == single.missing_scale_wound_probability


def test_two_shots_distribution_preserves_multidamage():
    result = get(IncomingMissile("a", "4+", 3, shots=2), wounds=2)
    assert len(result.incoming_wound_distribution) == 7
    assert sum(result.incoming_wound_distribution) == 1
    single = calculate_missing_scale_evidence(shooter_shoot_value="4+", missile_strength=3)
    assert result.expected_incoming_wounds == 2*single.expected_incoming_wounds
    assert result.elimination_probability > 0


def test_one_fate_pool_across_distinct_shooters():
    shots = (IncomingMissile("a", "2+", 3), IncomingMissile("b", "3+", 4))
    no_fate = get(*shots, wounds=2)
    with_fate = get(*shots, wounds=2, fate=2)
    assert with_fate.expected_incoming_wounds == no_fate.expected_incoming_wounds
    assert with_fate.elimination_probability < no_fate.elimination_probability


def test_non_smaug_rejected():
    with pytest.raises(ValueError, match="restricted"):
        calculate_smaug_missing_scale_volley(
            target_profile_id="TT_BILL",
            shooters=(IncomingMissile("a", "4+", 3),),
            state=DefensiveState(3))


def test_duplicate_identity_rejected():
    with pytest.raises(ValueError, match="distinct"):
        get(IncomingMissile("same", "4+", 3),IncomingMissile("same", "4+", 3))


def test_will_as_fate_not_assumed():
    with pytest.raises(ValueError, match="Will-as-Fate"):
        calculate_smaug_missing_scale_volley(
            target_profile_id="SMAUG",
            shooters=(IncomingMissile("a","4+",3),),
            state=DefensiveState(20,0,1))


def test_no_scoring_contamination():
    e=get(IncomingMissile("a","4+",3))
    assert e.dashboard_score is None and e.scenario_score is None
    assert e.status.startswith("bounded_")
