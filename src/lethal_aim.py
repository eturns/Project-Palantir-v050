from configured_profile import ConfiguredProfile
from lethal_aim_state import (
    LethalAimSpend,
    LethalAimState,
)
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from wound_modifier import WoundModifier


LETHAL_AIM_RULE_ID = "LETHAL_AIM"


def has_lethal_aim(
    profile: ConfiguredProfile,
) -> bool:
    return any(
        assignment.rule.id == LETHAL_AIM_RULE_ID
        for assignment in profile.effective_special_rules
    )


def can_use_lethal_aim(
    profile: ConfiguredProfile,
    state: LethalAimState,
    spend: LethalAimSpend,
    *,
    context: WoundContext | None = None,
) -> bool:
    if not has_lethal_aim(profile):
        return False

    if not state.can_spend_on(spend):
        return False

    if (
        spend is LethalAimSpend.TO_WOUND
        and (
            context is None
            or context.attack_type
            is not WoundAttackType.SHOOTING
        )
    ):
        return False

    return True


def get_lethal_aim_wound_modifier(
    profile: ConfiguredProfile,
    state: LethalAimState | None,
    *,
    context: WoundContext | None = None,
    spend: LethalAimSpend | None = None,
) -> WoundModifier:
    if (
        state is None
        or spend is not LethalAimSpend.TO_WOUND
    ):
        return WoundModifier()

    if not can_use_lethal_aim(
        profile,
        state,
        spend,
        context=context,
    ):
        return WoundModifier()

    return WoundModifier(
        to_wound=1,
    )