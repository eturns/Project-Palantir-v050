import pytest

from ability_tag_assignment import AbilityTagAssignment
from ability_tag_entity import AbilityTagEntity
from army import Army
from army_list import ArmyList
from army_metrics import calculate_army_metrics
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from database.rule_category import RuleCategory
from faction import Faction
from profile_metrics import calculate_profile_metrics
from profile_option import ProfileOption
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule


def create_profile():
    return Profile(
        id="GENERIC_HERO",
        name="Generic Hero",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="6+",
        might=2,
        will=1,
        fate=1,
        max_in_army=0,
    )


def create_army_list():
    return ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )


def create_hero_hunting_rule():
    hero_hunting_tag = AbilityTagEntity(
        id="HERO_HUNTING",
        name="Hero Hunting",
    )

    rule = SpecialRule(
        id="HERO_HUNTER",
        name="Hero Hunter",
        category=RuleCategory.OFFENCE,
    )

    rule.ability_tags.append(
        AbilityTagAssignment(
            tag=hero_hunting_tag,
            weight=1.75,
        )
    )

    return rule


def test_configured_profile_metrics_include_option_granted_rule():
    profile = create_profile()

    hero_hunting_rule = create_hero_hunting_rule()

    assignment = ProfileSpecialRuleAssignment(
        rule=hero_hunting_rule,
    )

    option = ProfileOption(
        id="HERO_HUNTER_OPTION",
        name="Hero Hunter",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    base_metrics = calculate_profile_metrics(
        profile,
    )

    configured_metrics = calculate_profile_metrics(
        configured_profile,
    )

    assert base_metrics.hero_hunting == pytest.approx(
        0.0,
    )

    assert configured_metrics.hero_hunting == pytest.approx(
        1.75,
    )


def test_army_metrics_distinguish_two_configurations_of_same_profile():
    profile = create_profile()

    hero_hunting_rule = create_hero_hunting_rule()

    assignment = ProfileSpecialRuleAssignment(
        rule=hero_hunting_rule,
    )

    option = ProfileOption(
        id="HERO_HUNTER_OPTION",
        name="Hero Hunter",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(option)

    plain = ConfiguredProfile(
        profile=profile,
    )

    hero_hunter = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    army = Army()

    army.add_configured_profile(
        plain,
    )

    army.add_configured_profile(
        hero_hunter,
    )

    metrics = calculate_army_metrics(
        army,
        create_army_list(),
    )

    assert len(army.entries) == 2

    assert (
        army.entries[0].profile
        is army.entries[1].profile
    )

    assert (
        army.entries[0].configured_profile
        is not army.entries[1].configured_profile
    )

    assert metrics.hero_hunting == pytest.approx(
        1.75,
    )


def test_army_entry_profile_metrics_uses_configured_profile():
    profile = create_profile()

    hero_hunting_rule = create_hero_hunting_rule()

    assignment = ProfileSpecialRuleAssignment(
        rule=hero_hunting_rule,
    )

    option = ProfileOption(
        id="HERO_HUNTER_OPTION",
        name="Hero Hunter",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
    )

    metrics = army.entries[0].profile_metrics()

    assert metrics.hero_hunting == pytest.approx(
        1.75,
    )