from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_state import MorgulBladeState


MORGUL_BLADE_WARGEAR_ID = "WG_MORGUL_BLADE"


def _configured_profile_from_combatant(
    combatant: ConfiguredProfile | FieldedModelFormState,
) -> ConfiguredProfile:
    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        return combatant.active_configured_profile

    return combatant


def _is_using_morgul_blade(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    selection: MeleeWeaponSelection | None,
    state: MorgulBladeState | None,
) -> bool:
    configured_profile = (
        _configured_profile_from_combatant(
            combatant,
        )
    )

    return (
        state is not None
        and state.active_this_combat
        and selection is not None
        and selection.wargear_id
        == MORGUL_BLADE_WARGEAR_ID
        and any(
            wargear.id
            == MORGUL_BLADE_WARGEAR_ID
            for wargear
            in configured_profile.effective_wargear
        )
    )


def get_morgul_blade_combat_strength(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    selection: MeleeWeaponSelection | None,
    state: MorgulBladeState | None,
) -> int:
    configured_profile = (
        _configured_profile_from_combatant(
            combatant,
        )
    )

    if _is_using_morgul_blade(
        combatant,
        selection=selection,
        state=state,
    ):
        return configured_profile.profile.strength

    return combatant.effective_strength


def get_morgul_blade_combat_attacks(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    selection: MeleeWeaponSelection | None,
    state: MorgulBladeState | None,
) -> int:
    configured_profile = (
        _configured_profile_from_combatant(
            combatant,
        )
    )

    if _is_using_morgul_blade(
        combatant,
        selection=selection,
        state=state,
    ):
        return configured_profile.profile.attacks

    return combatant.effective_attacks