from configured_profile import ConfiguredProfile
from wound_context import WoundContext
from wound_modifier import WoundModifier
from ring_of_power import RING_OF_POWER_WARGEAR_IDS
from wound_attack_type import WoundAttackType

HATRED_RULE_ID = 'HATRED'
BACKSTABBERS_RULE_ID = 'BACKSTABBERS'
MASTER_WANTS_RING_RULE_ID = 'YOU_HAVE_SOMETHING_MY_MASTER_WANTS'
PIERCING_TALONS_RULE_ID = 'PIERCING_TALONS'


def get_special_rule_wound_modifiers(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    context: WoundContext | None = None,
) -> tuple[WoundModifier, ...]:
    defender_keywords = defender.effective_keywords
    modifiers: list[WoundModifier] = []

    for assignment in attacker.effective_special_rules:
        if (
            assignment.rule.id == HATRED_RULE_ID
            and isinstance(assignment.parameter, str)
            and assignment.parameter.upper() in defender_keywords
        ):
            modifiers.append(WoundModifier(to_wound=1))

    attacker_rule_ids = {
        assignment.rule.id
        for assignment in attacker.effective_special_rules
    }

    if (
        BACKSTABBERS_RULE_ID in attacker_rule_ids
        and context is not None
        and context.defender_trapped
    ):
        modifiers.append(WoundModifier(to_wound=1))

    defender_wargear_ids = {
        wargear.id for wargear in defender.effective_wargear
    }
    attack_type = context.attack_type if context is not None else WoundAttackType.STRIKE

    if (
        MASTER_WANTS_RING_RULE_ID in attacker_rule_ids
        and attack_type is WoundAttackType.STRIKE
        and bool(defender_wargear_ids & RING_OF_POWER_WARGEAR_IDS)
    ):
        modifiers.append(WoundModifier(to_wound=1))

    # This bonus is *not* inferred from army composition or a model's
    # mobility; a War Bat must be explicitly identified as charging.
    if (
        PIERCING_TALONS_RULE_ID in attacker_rule_ids
        and attack_type is WoundAttackType.STRIKE
        and context is not None
        and context.attacker_charged is True
    ):
        modifiers.append(WoundModifier(to_wound=1))

    return tuple(modifiers)
