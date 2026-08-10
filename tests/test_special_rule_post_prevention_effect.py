from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from post_prevention_effect import PostPreventionEffect
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from special_rule_post_prevention_effect import (
    get_special_rule_post_prevention_effect,
)
from test_profiles import create_test_profile
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def test_attacker_without_drain_soul_has_no_post_prevention_effect():
    profile = create_test_profile(
        profile_id="TEST_ATTACKER",
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    context = WoundContext(
        attack_type=WoundAttackType.STRIKE,
    )

    result = get_special_rule_post_prevention_effect(
        attacker,
        context,
    )

    assert result == PostPreventionEffect.NONE


def test_drain_soul_applies_to_strikes():
    profile = create_test_profile(
        profile_id="TEST_NECROMANCER",
    )

    drain_soul = SpecialRule(
        id="DRAIN_SOUL",
        name="Drain Soul",
        category=RuleCategory.OFFENCE,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=drain_soul,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    context = WoundContext(
        attack_type=WoundAttackType.STRIKE,
    )

    result = get_special_rule_post_prevention_effect(
        attacker,
        context,
    )

    assert (
        result
        == PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO
    )


def test_drain_soul_does_not_apply_to_non_strike_attacks():
    profile = create_test_profile(
        profile_id="TEST_NECROMANCER",
    )

    drain_soul = SpecialRule(
        id="DRAIN_SOUL",
        name="Drain Soul",
        category=RuleCategory.OFFENCE,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=drain_soul,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    context = WoundContext(
        attack_type=WoundAttackType.SHOOTING,
    )

    result = get_special_rule_post_prevention_effect(
        attacker,
        context,
    )

    assert result == PostPreventionEffect.NONE