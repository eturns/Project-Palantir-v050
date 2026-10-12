"""DEV-077S-I2-E-B3 RED: Terror + contextual Harbinger integration.

Copy into tests/. The new keyword argument is intentionally missing
from the current production terror_charge.py.
"""
from fractions import Fraction

from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext
from database.rule_category import RuleCategory
from harbinger_courage import HarbingerInfluence
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from terror_charge import calculate_terror_charge_success_probability


def model(model_id, *, courage="7+", terror=False, fearless=False, harbinger_range=None):
    profile = Profile(
        id=model_id, name=model_id, points=10, movement=6, fight=3,
        shooting="4+", strength=3, defence=4, attacks=1, wounds=1,
        courage=courage, intelligence="7+", might=0, will=0, fate=0,
        max_in_army=0,
    )
    rules = []
    if terror:
        rules.append(("TERROR", None))
    if fearless:
        rules.append(("FEARLESS", None))
    if harbinger_range is not None:
        rules.append(("HARBINGER_OF_EVIL", harbinger_range))
    for rule_id, parameter in rules:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(id=rule_id, name=rule_id, category=RuleCategory.SPECIAL),
                parameter=parameter,
            )
        )
    return ConfiguredProfile(profile=profile)


def test_terror_plus_harbinger_in_range_uses_modified_probability():
    attacker = model("ATTACKER")
    defender = model("DEFENDER", terror=True, harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_harbinger_influences=(HarbingerInfluence(defender, 8),),
    ) == Fraction(15, 36)


def test_terror_plus_harbinger_out_of_range_is_unmodified():
    attacker = model("ATTACKER")
    defender = model("DEFENDER", terror=True, harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_harbinger_influences=(HarbingerInfluence(defender, 12.1),),
    ) == Fraction(21, 36)


def test_two_harbingers_in_range_do_not_stack():
    attacker = model("ATTACKER")
    defender = model("DEFENDER", terror=True, harbinger_range=12)
    ally = model("ALLY", harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_harbinger_influences=(
            HarbingerInfluence(defender, 5),
            HarbingerInfluence(ally, 7),
        ),
    ) == Fraction(15, 36)


def test_existing_explicit_modifier_and_harbinger_combine():
    attacker = model("ATTACKER")
    defender = model("DEFENDER", terror=True, harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_courage_context=CourageTestContext(roll_modifier=1),
        attacker_harbinger_influences=(HarbingerInfluence(defender, 8),),
    ) == Fraction(21, 36)


def test_fearless_attacker_ignores_terror_and_harbinger():
    attacker = model("ATTACKER", fearless=True)
    defender = model("DEFENDER", terror=True, harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_harbinger_influences=(HarbingerInfluence(defender, 8),),
    ) == Fraction(1, 1)


def test_harbinger_does_not_block_charge_without_terror():
    attacker = model("ATTACKER")
    defender = model("DEFENDER", harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_harbinger_influences=(HarbingerInfluence(defender, 8),),
    ) == Fraction(1, 1)


def test_harbinger_bearing_attacker_is_immune_to_enemy_harbinger():
    attacker = model("ATTACKER", harbinger_range=12)
    defender = model("DEFENDER", terror=True, harbinger_range=12)
    assert calculate_terror_charge_success_probability(
        attacker, defender,
        attacker_harbinger_influences=(HarbingerInfluence(defender, 8),),
    ) == Fraction(21, 36)
