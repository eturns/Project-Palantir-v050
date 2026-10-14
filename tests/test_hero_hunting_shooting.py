from fractions import Fraction
from types import SimpleNamespace
import pytest

from defensive_state import DefensiveState
from ranged_weapon_profile import RangedWeaponProfile
from shooting_eligibility import ShootingContext
from hero_hunting_shooting import calculate_hero_hunting_shooting_evidence


def profile(*, shoot="4+", defence=4, rules=()):
    weapon = SimpleNamespace(id="WG_ORC_BOW", special_rules=())
    return SimpleNamespace(
        effective_wargear=(weapon,), effective_shooting=shoot,
        effective_defence=defence,
        effective_special_rules=tuple(SimpleNamespace(rule=SimpleNamespace(id=r)) for r in rules),
        profile=SimpleNamespace(keywords=()),
    )


def evaluate(*, state=None, distance=12, los=True, moved=False,
             weapon=None, attacker=None, defender=None):
    return calculate_hero_hunting_shooting_evidence(
        attacker=attacker or profile(),
        defender=defender or profile(),
        weapon=weapon or RangedWeaponProfile("WG_ORC_BOW", 18, 2, 1),
        defender_state=state or DefensiveState(1),
        context=ShootingContext(moved_this_turn=moved, target_distance_inches=distance),
        clear_line_of_sight=los,
    )


def test_one_shot_matches_canonical_hit_times_wound():
    result = evaluate()
    assert result.shots == 1
    assert result.expected_wounds == result.wound_probability_per_shot
    assert result.elimination_probability == result.wound_probability_per_shot


def test_multiple_shots_use_distribution_not_expected_wounds():
    result = evaluate(attacker=profile(rules=("EXPERT_SHOT",)))
    p = result.wound_probability_per_shot
    assert result.shots == 2
    assert result.expected_wounds == 2*p
    assert result.elimination_probability == 1-(1-p)**2


def test_fate_reduces_elimination_probability():
    without = evaluate(state=DefensiveState(1))
    with_fate = evaluate(state=DefensiveState(1, remaining_fate=1))
    assert with_fate.elimination_probability < without.elimination_probability


@pytest.mark.parametrize("distance,los", [(None,True),(19,True),(12,False)])
def test_missing_range_out_of_range_or_no_los_rejected(distance,los):
    with pytest.raises(ValueError, match="Incomplete Hero Hunting"):
        evaluate(distance=distance,los=los)


def test_unowned_weapon_rejected():
    with pytest.raises(ValueError, match="not owned"):
        evaluate(weapon=RangedWeaponProfile("WG_ELF_BOW",24,3,1))


def test_will_conversion_is_not_silently_assumed():
    with pytest.raises(ValueError, match="Will-as-Fate"):
        evaluate(state=DefensiveState(1, remaining_will=1))


def test_incomplete_weapon_rejected():
    with pytest.raises(ValueError, match="ranged weapon mechanics"):
        evaluate(weapon=RangedWeaponProfile("WG_ORC_BOW"))
