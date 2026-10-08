from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile
from special_rule_wound_effect import (
    get_special_rule_wound_reroll,
)
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from wound_reroll import WoundReroll


POISONED_ATTACKS_RULE_ID = "POISONED_ATTACKS"


def get_shooting_special_rule_wound_reroll(
    *,
    attacker: ConfiguredProfile,
    weapon: RangedWeaponProfile,
) -> WoundReroll:
    profile_reroll = get_special_rule_wound_reroll(
        attacker,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    selected_wargear = next(
        (
            wargear
            for wargear in attacker.effective_wargear
            if wargear.id == weapon.wargear_id
        ),
        None,
    )

    weapon_has_poisoned_attacks = (
        selected_wargear is not None
        and any(
            rule.id == POISONED_ATTACKS_RULE_ID
            for rule in selected_wargear.special_rules
        )
    )

    return WoundReroll(
        reroll_failed=profile_reroll.reroll_failed,
        reroll_natural_ones=(
            profile_reroll.reroll_natural_ones
            or weapon_has_poisoned_attacks
        ),
    )