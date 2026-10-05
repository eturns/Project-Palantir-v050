from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


I_AM_THE_MASTER_RULE_ID = "I_AM_THE_MASTER"


def uses_i_am_the_master(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    context: WoundContext | None,
) -> bool:
    """
    Returns whether I am the Master should replace the
    normal To Wound target for this Strike.
    """

    if context is None:
        return False

    if not context.use_i_am_the_master:
        return False

    if (
        context.attack_type
        is not WoundAttackType.STRIKE
    ):
        return False

    attacker_rule_ids = {
        assignment.rule.id
        for assignment
        in attacker.effective_special_rules
    }

    if I_AM_THE_MASTER_RULE_ID not in attacker_rule_ids:
        return False

    return (
        defender.effective_heroic_status
        is HeroicStatus.HERO
    )