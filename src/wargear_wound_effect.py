from configured_profile import ConfiguredProfile
from wound_modifier import WoundModifier
from melee_weapon_selection import MeleeWeaponSelection


TWO_HANDED_WEAPON_ID = "WG_TWO_HANDED_WEAPON"


def get_wargear_wound_modifiers(
    configured_profile: ConfiguredProfile,
    selection: MeleeWeaponSelection | None = None,
) -> tuple[WoundModifier, ...]:
    modifiers = []

    for wargear in configured_profile.effective_wargear:
        if (
            wargear.id == TWO_HANDED_WEAPON_ID
            and (
                selection is None
                or selection.wargear_id
                == TWO_HANDED_WEAPON_ID
            )
        ):
            modifiers.append(
                WoundModifier(
                    to_wound=1,
                )
            )

    return tuple(modifiers)