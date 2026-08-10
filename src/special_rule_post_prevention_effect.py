from configured_profile import ConfiguredProfile
from post_prevention_effect import PostPreventionEffect
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


DRAIN_SOUL_RULE_ID = "DRAIN_SOUL"


def get_special_rule_post_prevention_effect(
    attacker: ConfiguredProfile,
    context: WoundContext,
) -> PostPreventionEffect:
    has_drain_soul = any(
        assignment.rule.id == DRAIN_SOUL_RULE_ID
        for assignment in attacker.profile.special_rules
    )

    if (
        has_drain_soul
        and context.attack_type == WoundAttackType.STRIKE
    ):
        return PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO

    return PostPreventionEffect.NONE