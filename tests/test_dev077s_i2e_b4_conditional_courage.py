"""DEV-077S-I2-E-B4 RED: contextual Bound in Shadow and Fearless.

New proposed entry point: contextual_courage.py. It must delegate the dice
calculation to the existing courage_test module rather than replace it.
"""
from fractions import Fraction

import pytest
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from courage_test import CourageTestContext
from contextual_courage import (
    CouragePositionContext,
    calculate_contextual_courage_success_probability,
)


def model(identifier="MODEL", *, courage="7+", rules=()):
    profile = Profile(
        id=identifier, name=identifier, points=10, movement=6,
        fight=3, shooting="4+", strength=3, defence=4,
        attacks=1, wounds=1, courage=courage, intelligence="7+",
        might=0, will=0, fate=0, max_in_army=0,
    )
    for rule_id in rules:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule_id, name=rule_id,
                             category=RuleCategory.SPECIAL)
        ))
    return ConfiguredProfile(profile=profile)


def probability(combatant, *, position=None, roll_modifier=0):
    return calculate_contextual_courage_success_probability(
        combatant,
        courage_context=CourageTestContext(roll_modifier=roll_modifier),
        position_context=position or CouragePositionContext(),
    )


def test_bound_near_sauron_auto_passes():
    m = model(rules=("BOUND_IN_SHADOW",))
    assert probability(m, position=CouragePositionContext(
        distance_to_sauron_inches=6,
    )) == Fraction(1, 1)


def test_bound_near_friendly_ringwraith_auto_passes():
    m = model(rules=("BOUND_IN_SHADOW",))
    assert probability(m, position=CouragePositionContext(
        distance_to_friendly_ringwraith_inches=4,
    )) == Fraction(1, 1)


def test_bound_outside_both_ranges_uses_dice():
    m = model(rules=("BOUND_IN_SHADOW",))
    assert probability(m, position=CouragePositionContext(
        distance_to_sauron_inches=6.01,
        distance_to_friendly_ringwraith_inches=9,
    )) == Fraction(21, 36)


def test_bound_with_unknown_positions_does_not_assume_support():
    m = model(rules=("BOUND_IN_SHADOW",))
    assert probability(m) == Fraction(21, 36)


def test_non_bound_model_cannot_borrow_auto_pass():
    m = model()
    assert probability(m, position=CouragePositionContext(
        distance_to_sauron_inches=1,
    )) == Fraction(21, 36)


def test_bound_auto_pass_overrides_negative_roll_modifier():
    m = model(rules=("BOUND_IN_SHADOW",))
    assert probability(m, roll_modifier=-3, position=CouragePositionContext(
        distance_to_friendly_ringwraith_inches=5,
    )) == Fraction(1, 1)


def test_fearless_passes_without_positional_support():
    m = model(rules=("FEARLESS",))
    assert probability(m, roll_modifier=-3) == Fraction(1, 1)


def test_out_of_range_modifier_remains_active():
    m = model(rules=("BOUND_IN_SHADOW",))
    assert probability(m, roll_modifier=-1, position=CouragePositionContext(
        distance_to_sauron_inches=7,
    )) == Fraction(15, 36)


@pytest.mark.parametrize("distance", [-0.01, -3])
def test_negative_distances_are_rejected(distance):
    m = model(rules=("BOUND_IN_SHADOW",))
    with pytest.raises(ValueError, match="Distance cannot be negative"):
        probability(m, position=CouragePositionContext(
            distance_to_sauron_inches=distance,
        ))
