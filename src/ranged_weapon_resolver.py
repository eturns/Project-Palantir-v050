from configured_profile import ConfiguredProfile
from ranged_weapon_profile import (
    RANGED_WEAPON_PROFILES,
    RangedWeaponProfile,
)


def resolve_ranged_weapon(
    profile: ConfiguredProfile,
) -> RangedWeaponProfile | None:
    """
    Resolves the ranged weapon currently equipped by a
    configured Profile.

    Returns None when the configured model has no recognised
    ranged weapon definition.
    """

    for wargear in profile.effective_wargear:
        ranged_weapon = RANGED_WEAPON_PROFILES.get(
            wargear.id,
        )

        if ranged_weapon is not None:
            return ranged_weapon

    return None