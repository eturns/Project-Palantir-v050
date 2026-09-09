from army import Army
from army_list import ArmyList
from battlefield_army_evidence_builder import (
    build_army_battlefield_evidence,
)
from battlefield_profile_evidence_builder import (
    build_profile_battlefield_evidence,
)
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from database.rule_category import RuleCategory
from faction import Faction
from profile_option import ProfileOption
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
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


def create_army_list():
    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    return ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
    )


def test_profile_evidence_uses_configured_granted_special_rule():
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

    evidence = (
        build_profile_battlefield_evidence(
            configured_profile,
        )
    )

    assert profile.special_rules == []

    assert [
        assignment.rule.id
        for assignment
        in evidence.available_special_rules
    ] == [
        "TERROR",
    ]


def test_profile_evidence_respects_configured_removed_special_rule():
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

    evidence = (
        build_profile_battlefield_evidence(
            configured_profile,
        )
    )

    assert len(profile.special_rules) == 1
    assert evidence.available_special_rules == []


def test_profile_evidence_preserves_base_profile_compatibility():
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

    evidence = (
        build_profile_battlefield_evidence(
            profile,
        )
    )

    assert [
        assignment.rule.id
        for assignment
        in evidence.available_special_rules
    ] == [
        "TERROR",
    ]


def test_army_evidence_uses_each_entrys_configured_special_rules():
    terror = SpecialRule(
        id="TERROR",
        name="Terror",
        category=RuleCategory.SPECIAL,
    )

    dominant = SpecialRule(
        id="DOMINANT",
        name="Dominant",
        category=RuleCategory.SPECIAL,
    )

    terror_assignment = (
        ProfileSpecialRuleAssignment(
            rule=terror,
        )
    )

    dominant_assignment = (
        ProfileSpecialRuleAssignment(
            rule=dominant,
            parameter=2,
        )
    )

    profile = create_profile()

    terror_option = ProfileOption(
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

    dominant_option = ProfileOption(
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

    profile.profile_options.extend(
        (
            terror_option,
            dominant_option,
        )
    )

    terror_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            terror_option,
        ),
    )

    dominant_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            dominant_option,
        ),
    )

    army = Army()

    army.add_configured_profile(
        terror_profile,
    )

    army.add_configured_profile(
        dominant_profile,
    )

    evidence = build_army_battlefield_evidence(
        army,
        create_army_list(),
    )

    rule_ids = {
        assignment.rule.id
        for assignment
        in evidence.available_special_rules
    }

    assert rule_ids == {
        "TERROR",
        "DOMINANT",
    }