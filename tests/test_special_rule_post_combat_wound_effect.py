from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from post_combat_wound_effect import (
    PostCombatWoundEffect,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from special_rule_post_combat_wound_effect import (
    get_special_rule_post_combat_wound_effect,
)


def create_test_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_venom_grants_additional_wound_on_six():
    profile = create_test_profile()

    venom = SpecialRule(
        id="VENOM",
        name="Venom",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=venom,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    assert get_special_rule_post_combat_wound_effect(
        attacker,
    ) == PostCombatWoundEffect(
        additional_wound_on_roll=6,
    )


def test_profile_without_venom_has_no_post_combat_wound_effect():
    attacker = ConfiguredProfile(
        profile=create_test_profile(),
    )

    assert get_special_rule_post_combat_wound_effect(
        attacker,
    ) == PostCombatWoundEffect()