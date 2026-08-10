from configured_profile import ConfiguredProfile
from wound_reroll import WoundReroll
from melee_weapon_selection import MeleeWeaponSelection
from wound_attack_type import WoundAttackType
from wound_context import WoundContext

BANE_OF_KINGS_RULE_ID = "BANE_OF_KINGS"
VENOM_RULE_ID = "VENOM"
POISONED_ATTACKS_RULE_ID = "POISONED_ATTACKS"
ANCIENT_ENEMIES_RULE_ID = "ANCIENT_ENEMIES"
SLAYER_OF_MEN_RULE_ID = "SLAYER_OF_MEN"


def get_special_rule_wound_reroll(
    configured_profile: ConfiguredProfile,
    selection: MeleeWeaponSelection | None = None,
    defender: ConfiguredProfile | None = None,
    context: WoundContext | None = None,
) -> WoundReroll:
    rule_ids = {
        assignment.rule.id
        for assignment
        in configured_profile.profile.special_rules
    }

    defender_keywords = set()

    if defender is not None:
        defender_keywords = {
            keyword.upper()
            for keyword in defender.profile.keywords
        }

    has_ancient_enemies_match = any(
        assignment.rule.id == ANCIENT_ENEMIES_RULE_ID
        and isinstance(assignment.parameter, str)
        and assignment.parameter.upper() in defender_keywords
        for assignment in configured_profile.profile.special_rules
    )


    selected_weapon_rule_ids = set()

    if selection is not None:
        selected_weapon = next(
            (
                wargear
                for wargear
                in configured_profile.effective_wargear
                if wargear.id == selection.wargear_id
            ),
            None,
        )

        if selected_weapon is not None:
            selected_weapon_rule_ids = {
                rule.id
                for rule in selected_weapon.special_rules
            }

    attack_type = (
        context.attack_type
        if context is not None
        else WoundAttackType.STRIKE
    )

    has_slayer_of_men_match = (
        SLAYER_OF_MEN_RULE_ID in rule_ids
        and "HERO" in defender_keywords
        and attack_type == WoundAttackType.STRIKE
    )

    return WoundReroll(
        reroll_failed=(
            BANE_OF_KINGS_RULE_ID in rule_ids
            or (
                VENOM_RULE_ID in rule_ids
                and attack_type == WoundAttackType.STRIKE
            )
            or has_slayer_of_men_match
        ),
        reroll_natural_ones=(
            POISONED_ATTACKS_RULE_ID in rule_ids
            or (
                POISONED_ATTACKS_RULE_ID
                in selected_weapon_rule_ids
                and attack_type == WoundAttackType.STRIKE
            )
            or has_ancient_enemies_match
        ),
    )