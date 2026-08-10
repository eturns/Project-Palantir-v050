from configured_profile import ConfiguredProfile
from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)
from wound_context import WoundContext


MIGHTY_BLOW_RULE_ID = "MIGHTY_BLOW"
XBANE_RULE_ID = "XBANE"
EXECUTIONER_RULE_ID = "EXECUTIONER"


def get_special_rule_strike_damage(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile | None = None,
    context: WoundContext | None = None,
) -> StrikeDamage:
    if defender is not None:
        defender_keywords = {
            keyword.upper()
            for keyword in defender.profile.keywords
        }

        has_xbane_match = any(
            assignment.rule.id == XBANE_RULE_ID
            and isinstance(assignment.parameter, str)
            and assignment.parameter.upper() in defender_keywords
            for assignment in attacker.profile.special_rules
        )

        if has_xbane_match:
            return StrikeDamage(
                damage_type=StrikeDamageType.D3,
            )


    has_executioner_trigger = (
        context is not None
        and context.attacker_natural_duel_roll == 6
        and any(
            assignment.rule.id == EXECUTIONER_RULE_ID
            for assignment in attacker.profile.special_rules
        )
    )

    if has_executioner_trigger:
        return StrikeDamage(
            wounds_per_successful_strike=2,
        )
    
    has_mighty_blow = any(
        assignment.rule.id == MIGHTY_BLOW_RULE_ID
        for assignment in attacker.profile.special_rules
    )

    if has_mighty_blow:
        return StrikeDamage(
            wounds_per_successful_strike=2,
        )

    return StrikeDamage()