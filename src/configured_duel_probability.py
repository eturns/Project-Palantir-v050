from configured_profile import ConfiguredProfile
from duel_probability import (
    calculate_basic_duel_probability,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from melee_weapon_selection import MeleeWeaponSelection
from roll_modifier_effect_resolver import (
    resolved_duel_modifier,
)
from wargear_mechanical_effect_definitions import (
    get_wargear_mechanical_effect_definitions,
)


def calculate_configured_duel_probability(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    attacker_selection: MeleeWeaponSelection | None = None,
    defender_selection: MeleeWeaponSelection | None = None,
    attacker_additional_burly: bool = False,
    defender_additional_burly: bool = False,
):
    attacker_definitions = tuple(
        definition
        for definition in get_wargear_mechanical_effect_definitions(
            attacker,
            selection=attacker_selection,
            additional_burly=attacker_additional_burly,
        )
        if (
            definition.effect.target
            is MechanicalEffectTarget.DUEL_ROLL
        )
    )

    defender_definitions = tuple(
        definition
        for definition in get_wargear_mechanical_effect_definitions(
            defender,
            selection=defender_selection,
            additional_burly=defender_additional_burly,
        )
        if (
            definition.effect.target
            is MechanicalEffectTarget.DUEL_ROLL
        )
    )

    attacker_modifier = resolved_duel_modifier(
        attacker_definitions,
    )
    defender_modifier = resolved_duel_modifier(
        defender_definitions,
    )

    return calculate_basic_duel_probability(
        attacker_attacks=attacker.profile.attacks,
        attacker_fight=attacker.profile.fight,
        defender_attacks=defender.profile.attacks,
        defender_fight=defender.profile.fight,
        attacker_modifier=attacker_modifier,
        defender_modifier=defender_modifier,
    )