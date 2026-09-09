from army import Army
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from database.rule_category import RuleCategory
from profile_option import ProfileOption
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from repeated_ability_scaling import (
    count_models_with_parameterised_special_rule,
    count_models_with_special_rule,
    highest_special_rule_parameter,
)
from special_rule import SpecialRule


def create_profile(
    special_rules=None,
):
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    if special_rules:
        profile.special_rules.extend(
            special_rules,
        )

    return profile


def test_count_models_with_special_rule_uses_configured_granted_rule():
    terror = SpecialRule(
        id="TERROR",
        name="Terror",
        category=RuleCategory.SPECIAL,
    )

    terror_assignment = (
        ProfileSpecialRuleAssignment(
            rule=terror,
        )
    )

    profile = create_profile()

    option = ProfileOption(
        id="TERROR_OPTION",
        name="Terror Option",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    terror_assignment,
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
        quantity=3,
    )

    assert profile.special_rules == []

    assert (
        count_models_with_special_rule(
            army,
            "TERROR",
        )
        == 3
    )


def test_count_models_with_special_rule_respects_configured_removed_rule():
    terror = SpecialRule(
        id="TERROR",
        name="Terror",
        category=RuleCategory.SPECIAL,
    )

    terror_assignment = (
        ProfileSpecialRuleAssignment(
            rule=terror,
        )
    )

    profile = create_profile(
        special_rules=[
            terror_assignment,
        ],
    )

    option = ProfileOption(
        id="REMOVE_TERROR",
        name="Remove Terror",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                removed_special_rule_ids=(
                    "TERROR",
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
        quantity=2,
    )

    assert len(profile.special_rules) == 1

    assert (
        count_models_with_special_rule(
            army,
            "TERROR",
        )
        == 0
    )


def test_parameterised_special_rule_queries_use_configured_rules():
    dominant = SpecialRule(
        id="DOMINANT",
        name="Dominant",
        category=RuleCategory.SPECIAL,
    )

    dominant_assignment = (
        ProfileSpecialRuleAssignment(
            rule=dominant,
            parameter=3,
        )
    )

    profile = create_profile()

    option = ProfileOption(
        id="DOMINANT_OPTION",
        name="Dominant Option",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    dominant_assignment,
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
        quantity=2,
    )

    assert (
        count_models_with_parameterised_special_rule(
            army,
            "DOMINANT",
        )
        == 2
    )

    assert (
        highest_special_rule_parameter(
            army,
            "DOMINANT",
        )
        == 3
    )