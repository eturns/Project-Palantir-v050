"""DEV-077-GUN-C5-A: generic Chittering Hordes support permission.

The caller must establish physical support position/line of contact. This
module supplies the rule-specific permission and an ordinary supporting
CombatParticipant. It does not invent geometry or change spear support.
"""
from configured_profile import ConfiguredProfile
from combat_participant import CombatParticipant
from melee_weapon_selection import MeleeWeaponSelection

RULE_ID = "CHITTERING_HORDES"
TWO_HANDED_ID = "WG_TWO_HANDED_WEAPON"


def has_chittering_hordes(model: ConfiguredProfile) -> bool:
    return any(
        assignment.rule.id == RULE_ID
        for assignment in model.effective_special_rules
    )


def can_chittering_hordes_support(
    supporter: ConfiguredProfile,
    supported: ConfiguredProfile,
    *,
    valid_support_position: bool,
    selected_weapon: MeleeWeaponSelection | None = None,
) -> bool:
    """Support allowed only between two rule-holders in valid positions.

    Selecting a two-handed weapon while using this ability is prohibited.
    Unknown positioning is not treated as permission.
    """
    if type(valid_support_position) is not bool:
        raise TypeError("valid_support_position must be a bool")
    if not valid_support_position:
        return False
    if not has_chittering_hordes(supporter) or not has_chittering_hordes(supported):
        return False
    if selected_weapon is not None:
        if not isinstance(selected_weapon, MeleeWeaponSelection):
            raise TypeError("selected_weapon must be MeleeWeaponSelection or None")
        held = {item.id for item in supporter.effective_wargear}
        if selected_weapon.wargear_id not in held:
            raise ValueError("Selected weapon is not held by supporter")
        if selected_weapon.wargear_id == TWO_HANDED_ID:
            return False
    return True


def make_chittering_hordes_support_participant(
    supporter: ConfiguredProfile,
    supported: ConfiguredProfile,
    *,
    valid_support_position: bool,
    selected_weapon: MeleeWeaponSelection | None = None,
) -> CombatParticipant:
    """Represent permitted support in the existing multi-model duel model."""
    if not can_chittering_hordes_support(
        supporter, supported,
        valid_support_position=valid_support_position,
        selected_weapon=selected_weapon,
    ):
        raise ValueError("Chittering Hordes support is not permitted")
    return CombatParticipant(
        profile=supporter.profile,
        duel_dice=1,
        contributes_fight=True,
        can_make_strikes=False,
    )
