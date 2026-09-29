from profiles import Profile
from profile_spell_assignment import ProfileSpellAssignment
from configured_profile import ConfiguredProfile
from ranged_wargear import RANGED_WARGEAR_IDS

def ability_is_available(
    profile: Profile,
    ability,
) -> bool:
    """
    Returns True if the Profile can use the supplied ability.
    """

    if isinstance(
        ability,
        ProfileSpellAssignment,
    ):
        ability = ability.spell

    if not ability.prerequisites:
        return True

    for prerequisite in ability.prerequisites:

        if prerequisite.id == "HAS_RANGED_WEAPON":

            if not _has_ranged_weapon(profile):
                return False

        elif prerequisite.id == "HAS_SPELLS":

            if not _has_spells(profile):
                return False

    return True

def _has_ranged_weapon(
    profile: Profile | ConfiguredProfile,
) -> bool:
    if isinstance(profile, ConfiguredProfile):
        wargear = profile.effective_wargear
    else:
        wargear = profile.default_wargear

    return any(
        item.id in RANGED_WARGEAR_IDS
        for item in wargear
    )

def _has_spells(
    profile: Profile | ConfiguredProfile,
) -> bool:
    if isinstance(profile, ConfiguredProfile):
        profile = profile.profile

    return len(profile.spells) > 0