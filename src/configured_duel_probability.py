from configured_profile import ConfiguredProfile
from duel_probability import (
    calculate_basic_duel_probability,
)
from wargear_duel_effect import (
    get_wargear_duel_modifiers,
)
from melee_weapon_selection import MeleeWeaponSelection

def calculate_configured_duel_probability(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    attacker_selection: MeleeWeaponSelection | None = None,
    defender_selection: MeleeWeaponSelection | None = None,
    attacker_additional_burly: bool = False,
    defender_additional_burly: bool = False,
):
    attacker_modifiers = get_wargear_duel_modifiers(
        attacker,
        selection=attacker_selection,
        additional_burly=attacker_additional_burly,
    )

    defender_modifiers = get_wargear_duel_modifiers(
        defender,
        selection=defender_selection,
        additional_burly=defender_additional_burly,
    )

    attacker_modifier = (
        attacker_modifiers[0]
        if attacker_modifiers
        else None
    )

    defender_modifier = (
        defender_modifiers[0]
        if defender_modifiers
        else None
    )

    return calculate_basic_duel_probability(
        attacker_attacks=attacker.profile.attacks,
        attacker_fight=attacker.profile.fight,
        defender_attacks=defender.profile.attacks,
        defender_fight=defender.profile.fight,
        attacker_modifier=attacker_modifier,
        defender_modifier=defender_modifier,
    )