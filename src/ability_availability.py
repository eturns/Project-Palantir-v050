from profiles import Profile
from profile_spell_assignment import ProfileSpellAssignment

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
    profile: Profile,
) -> bool:
    """
    Returns True if the Profile possesses a ranged weapon.
    """

    return False

def _has_spells(
    profile: Profile,
) -> bool:
    """
    Returns True if the Profile can cast spells.
    """

    return len(profile.spells) > 0