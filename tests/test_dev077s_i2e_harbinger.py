"""DEV-077S-I2-E-B2 RED tests for Harbinger of Evil.

Place in tests/. Expected to fail until src/harbinger_courage.py exists.
This is a proposed mechanical interface; no production changes yet.
"""
from fractions import Fraction

from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from courage_test import CourageTestContext, calculate_courage_test_success_probability

from harbinger_courage import (
    HarbingerInfluence,
    calculate_harbinger_roll_modifier,
)


def make_model(model_id, *, courage="7+", harbinger_range=None, fearless=False):
    profile = Profile(
        id=model_id, name=model_id, points=10, movement=6, fight=3,
        shooting="4+", strength=3, defence=4, attacks=1, wounds=1,
        courage=courage, intelligence="7+", might=0, will=0, fate=0,
        max_in_army=0,
    )
    if harbinger_range is not None:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="HARBINGER_OF_EVIL", name="Harbinger of Evil",
                    category=RuleCategory.SPECIAL,
                ),
                parameter=harbinger_range,
            )
        )
    if fearless:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="FEARLESS", name="Fearless",
                    category=RuleCategory.SPECIAL,
                ),
            )
        )
    return ConfiguredProfile(profile=profile)


def test_one_harbinger_in_range_applies_minus_one():
    target = make_model("TARGET")
    source = make_model("SOURCE", harbinger_range=12)
    modifier = calculate_harbinger_roll_modifier(
        target,
        (HarbingerInfluence(provider=source, distance_inches=8),),
    )
    assert modifier == -1
    assert calculate_courage_test_success_probability(
        target, CourageTestContext(roll_modifier=modifier)
    ) == Fraction(15, 36)


def test_harbinger_outside_range_has_no_effect():
    target = make_model("TARGET")
    source = make_model("SOURCE", harbinger_range=12)
    assert calculate_harbinger_roll_modifier(
        target,
        (HarbingerInfluence(provider=source, distance_inches=12.01),),
    ) == 0


def test_harbinger_exactly_at_range_boundary_applies():
    target = make_model("TARGET")
    source = make_model("SOURCE", harbinger_range=12)
    assert calculate_harbinger_roll_modifier(
        target,
        (HarbingerInfluence(provider=source, distance_inches=12),),
    ) == -1


def test_multiple_harbingers_do_not_stack_by_default():
    target = make_model("TARGET")
    source_a = make_model("A", harbinger_range=12)
    source_b = make_model("B", harbinger_range=12)
    assert calculate_harbinger_roll_modifier(
        target,
        (
            HarbingerInfluence(provider=source_a, distance_inches=5),
            HarbingerInfluence(provider=source_b, distance_inches=6),
        ),
    ) == -1


def test_harbinger_models_ignore_enemy_harbinger():
    target = make_model("TARGET", harbinger_range=12)
    source = make_model("SOURCE", harbinger_range=12)
    assert calculate_harbinger_roll_modifier(
        target,
        (HarbingerInfluence(provider=source, distance_inches=5),),
    ) == 0


def test_source_without_harbinger_does_not_apply_penalty():
    target = make_model("TARGET")
    source = make_model("SOURCE")
    assert calculate_harbinger_roll_modifier(
        target,
        (HarbingerInfluence(provider=source, distance_inches=5),),
    ) == 0


def test_fearless_target_still_automatically_passes():
    target = make_model("TARGET", fearless=True)
    source = make_model("SOURCE", harbinger_range=12)
    modifier = calculate_harbinger_roll_modifier(
        target,
        (HarbingerInfluence(provider=source, distance_inches=5),),
    )
    assert calculate_courage_test_success_probability(
        target, CourageTestContext(roll_modifier=modifier)
    ) == Fraction(1, 1)
