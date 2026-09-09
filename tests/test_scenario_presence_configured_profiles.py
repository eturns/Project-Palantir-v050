import pytest

from army import Army
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from database.rule_category import RuleCategory
from profile_option import ProfileOption
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from scenario_presence import (
    calculate_army_scenario_presence,
    calculate_profile_scenario_presence,
)
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


def create_dominant_rule(
    value: int,
):
    dominant = SpecialRule(
        id="DOMINANT",
        name="Dominant",
        category=RuleCategory.SPECIAL,
    )

    return ProfileSpecialRuleAssignment(
        rule=dominant,
        parameter=value,
    )


def test_configured_granted_dominant_changes_profile_scenario_presence():
    profile = create_profile()

    dominant_assignment = create_dominant_rule(
        3,
    )

    option = ProfileOption(
        id="DOMINANT_OPTION",
        name="Dominant Option",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    dominant_assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(
        option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    dominant = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    assert calculate_profile_scenario_presence(
        plain,
    ) == 1

    assert calculate_profile_scenario_presence(
        dominant,
    ) == 3


def test_configured_removed_dominant_stops_contributing():
    profile = create_profile()

    dominant_assignment = create_dominant_rule(
        3,
    )

    profile.special_rules.append(
        dominant_assignment,
    )

    option = ProfileOption(
        id="REMOVE_DOMINANT",
        name="Remove Dominant",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                removed_special_rule_ids=(
                    "DOMINANT",
                ),
            ),
        ),
    )

    profile.profile_options.append(
        option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    removed = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    assert calculate_profile_scenario_presence(
        plain,
    ) == 3

    assert calculate_profile_scenario_presence(
        removed,
    ) == 1


def test_profile_scenario_presence_preserves_base_profile_compatibility():
    profile = create_profile()

    dominant_assignment = create_dominant_rule(
        2,
    )

    profile.special_rules.append(
        dominant_assignment,
    )

    base_result = calculate_profile_scenario_presence(
        profile,
    )

    configured_result = calculate_profile_scenario_presence(
        ConfiguredProfile(
            profile=profile,
        ),
    )

    assert base_result == 2
    assert configured_result == base_result


def test_same_profile_with_two_configurations_remains_distinct_in_army_presence():
    profile = create_profile()

    dominant_assignment = create_dominant_rule(
        3,
    )

    option = ProfileOption(
        id="DOMINANT_OPTION",
        name="Dominant Option",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    dominant_assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(
        option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    dominant = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    result = calculate_army_scenario_presence(
        (
            plain,
            dominant,
        ),
    )

    assert (
        plain.profile
        is dominant.profile
    )

    assert result == 4


def test_army_entries_can_expand_as_distinct_configured_profiles():
    profile = create_profile()

    dominant_assignment = create_dominant_rule(
        3,
    )

    option = ProfileOption(
        id="DOMINANT_OPTION",
        name="Dominant Option",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    dominant_assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(
        option,
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=profile,
        ),
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=profile,
            selected_options=(
                option,
            ),
        ),
    )

    profiles = tuple(
        entry.configured_profile
        for entry in army.entries
        for _ in range(entry.quantity)
    )

    assert calculate_army_scenario_presence(
        profiles,
    ) == 4