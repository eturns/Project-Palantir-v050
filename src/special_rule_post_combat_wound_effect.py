from configured_profile import ConfiguredProfile
from post_combat_wound_effect import (
    PostCombatWoundEffect,
)


VENOM_RULE_ID = "VENOM"


def get_special_rule_post_combat_wound_effect(
    attacker: ConfiguredProfile,
) -> PostCombatWoundEffect:
    has_venom = any(
        assignment.rule.id == VENOM_RULE_ID
        for assignment in attacker.profile.special_rules
    )

    if has_venom:
        return PostCombatWoundEffect(
            additional_wound_on_roll=6,
        )

    return PostCombatWoundEffect()