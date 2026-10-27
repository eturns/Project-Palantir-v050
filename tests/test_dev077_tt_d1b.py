"""DEV-077-TT-D1B: rule-aware shooting checks. Run from repo root."""
from fractions import Fraction
import pytest
from configured_profile import ConfiguredProfile
from profiles import Profile
from special_rule import SpecialRule
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from database.rule_category import RuleCategory
from ranged_weapon_resolver import resolve_ranged_weapon
from shooting_eligibility import ShootingContext, can_shoot
from shooting_wound_probability import get_expected_shooting_wounds
from three_trolls_shooting import (
    THROW_STONES_WEAPON, ModelObstruction, large_target_in_the_way_rolls,
)


def profile(pid="TEST", rules=(), shoot="4+"):
    p = Profile(id=pid, name=pid, points=40, movement=6, fight=4,
        shooting=shoot, strength=4, defence=6, attacks=1, wounds=2,
        courage="6+", intelligence="6+", might=0, will=0, fate=0,
        max_in_army=1)
    for rule_id in rules:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule_id, name=rule_id, category=RuleCategory.SPECIAL)))
    return ConfiguredProfile(profile=p)


@pytest.mark.parametrize("pid", ["BILL", "BERT", "TOM"])
def test_throw_stones_rule_resolves_without_wargear(pid):
    shooter = profile(pid, ("THROW_STONES",))
    assert resolve_ranged_weapon(shooter) == THROW_STONES_WEAPON
    assert resolve_ranged_weapon(shooter).strength == 8
    assert resolve_ranged_weapon(shooter).range_inches == 12


def test_unassigned_rule_is_not_credited():
    assert resolve_ranged_weapon(profile()) is None


def test_cannot_throw_after_moving():
    p = profile(rules=("THROW_STONES",))
    assert not can_shoot(shooter=p, weapon=resolve_ranged_weapon(p),
                         context=ShootingContext(moved_this_turn=True))


def test_can_throw_when_stationary_and_within_range():
    p = profile(rules=("THROW_STONES",))
    assert can_shoot(shooter=p, weapon=resolve_ranged_weapon(p),
                     context=ShootingContext(target_distance_inches=12))
    assert not can_shoot(shooter=p, weapon=resolve_ranged_weapon(p),
                         context=ShootingContext(target_distance_inches=12.1))


def test_stone_uses_existing_hit_wound_engine():
    attacker = profile(rules=("THROW_STONES",))
    defender = profile("TARGET")
    result = get_expected_shooting_wounds(attacker=attacker, defender=defender,
                                           weapon=resolve_ranged_weapon(attacker))
    assert isinstance(result, Fraction)
    assert Fraction(0) < result <= Fraction(1)


def test_large_target_ignores_small_models_not_large_models():
    target = profile(rules=("LARGE_TARGET",))
    rolls = large_target_in_the_way_rolls(
        defender=target, terrain_required_rolls=(5,),
        model_obstructions=(
            ModelObstruction(4, frozenset({"INFANTRY"})),
            ModelObstruction(3, frozenset({"MONSTER"})),
            ModelObstruction(4, frozenset({"SIEGE_ENGINE"})),
            ModelObstruction(5, frozenset({"WAR_BEAST"})),
        ), shooting_into_combat_required_roll=4)
    assert rolls == (5, 3, 4, 5, 4)


def test_non_large_target_keeps_all_models():
    assert large_target_in_the_way_rolls(defender=profile(),
        model_obstructions=(ModelObstruction(4, frozenset({"INFANTRY"})),)) == (4,)


def test_large_target_does_not_ignore_terrain_or_combat():
    assert large_target_in_the_way_rolls(defender=profile(rules=("LARGE_TARGET",)),
        terrain_required_rolls=(5,), shooting_into_combat_required_roll=4) == (5, 4)


@pytest.mark.parametrize("roll", [0, 1, 7])
def test_invalid_obstruction_roll_rejected(roll):
    with pytest.raises(ValueError):
        ModelObstruction(roll, frozenset({"INFANTRY"}))
