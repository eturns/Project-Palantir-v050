"""DEV-077S-I2-D-B3: characterization of current mobility-tag behaviour.

This file deliberately does not assert that tag weights are movement inches.
It records the baseline before rules-text-grounded mechanical alignment.
"""
import pytest

from army import Army
from army_manoeuvrability import calculate_army_manoeuvrability
from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule


def _profile(name: str, rule_id: str | None = None, weight: float = 0.0) -> Profile:
    profile = Profile(
        id=name,
        name=name,
        points=10,
        movement=6,
        base_size_mm=25,
        fight=3,
        shooting="4+",
        strength=3,
        defence=3,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )
    if rule_id is not None:
        rule = SpecialRule(id=rule_id, name=rule_id, category=RuleCategory.MOBILITY)
        rule.ability_tags.append(
            AbilityTagAssignment(tag=AbilityTagEntity(id="MOBILITY", name="Mobility"), weight=weight)
        )
        profile.special_rules.append(ProfileSpecialRuleAssignment(rule=rule))
    return profile


@pytest.mark.parametrize(
    ("rule_id", "weight"),
    [
        ("SPECTRAL_WALK", 1.5),
        ("UNNATURAL_SPEED", 1.5),
        ("SWIFT_MOVEMENT", 1.25),
    ],
)
def test_unconditional_tag_current_baseline(rule_id, weight):
    army = Army()
    army.add_profile(_profile("MODEL", rule_id, weight))
    assert calculate_army_manoeuvrability(army) == pytest.approx(6.0 + weight)


def test_spiritual_displacement_single_model_current_baseline():
    army = Army()
    army.add_profile(_profile("SINGLE", "SPIRITUAL_DISPLACEMENT", 1.5))
    assert calculate_army_manoeuvrability(army) == pytest.approx(6.0)


def test_spiritual_displacement_two_models_current_baseline():
    army = Army()
    army.add_profile(_profile("PAIR", "SPIRITUAL_DISPLACEMENT", 1.5), quantity=2)
    assert calculate_army_manoeuvrability(army) == pytest.approx(6.75)


def test_tag_weight_is_not_raw_movement_distance():
    """Current tag changes assessment, not the profile's Movement characteristic."""
    army = Army()
    profile = _profile("SWIFT", "SWIFT_MOVEMENT", 1.25)
    army.add_profile(profile)
    assert army.entries[0].configured_profile.effective_movement == 6
    assert calculate_army_manoeuvrability(army) == pytest.approx(7.25)
