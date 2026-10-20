"""Gundabad Troll Crushing Club: weapon-conditional damage and knockdown.

A non-Gundabad attacker, including a lightweight combat evidence object, has
no Crushing Club effect. Other combat rules are handled by their own resolvers.
"""
from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from melee_weapon_selection import MeleeWeaponSelection
from strike_damage import StrikeDamage


CRUSHING_CLUB_ID = "WG_CRUSHING_CLUB"
GUNDABAD_TROLL_ID = "GUNDABAD_TROLL"


def uses_crushing_club(
    attacker: ConfiguredProfile,
    selection: MeleeWeaponSelection | None = None,
) -> bool:
    """Require the canonical Troll, equipped club, and compatible selection.

    Some existing diagnostic callers use combat-only objects without a
    ``profile`` or ``effective_wargear`` attribute. Such an attacker cannot
    establish the Crushing Club's prerequisites and therefore gets no bonus.
    """
    profile = getattr(attacker, "profile", None)
    if getattr(profile, "id", None) != GUNDABAD_TROLL_ID:
        return False

    equipment = getattr(attacker, "effective_wargear", ())
    if not any(
        getattr(item, "id", None) == CRUSHING_CLUB_ID
        for item in equipment
    ):
        return False

    if selection is not None and selection.wargear_id != CRUSHING_CLUB_ID:
        return False

    return True


def crushing_club_strike_damage(
    attacker: ConfiguredProfile,
    selection: MeleeWeaponSelection | None = None,
) -> StrikeDamage | None:
    """Each successful Crushing Club strike causes two wounds before Fate."""
    if uses_crushing_club(attacker, selection):
        return StrikeDamage(wounds_per_successful_strike=2)
    return None


@dataclass(frozen=True)
class CrushingClubKnockdown:
    """End-of-combat knockdown, resolved only for an eligible unslain victim."""

    eligible: bool

    def resolve(self, natural_roll: int) -> bool:
        if (
            isinstance(natural_roll, bool)
            or not isinstance(natural_roll, int)
            or not 1 <= natural_roll <= 6
        ):
            raise ValueError("Knockdown requires a natural D6 result from 1 to 6.")
        return self.eligible and natural_roll >= 3


def crushing_club_knockdown(
    attacker: ConfiguredProfile,
    *,
    struck: bool,
    slain: bool,
    selection: MeleeWeaponSelection | None = None,
) -> CrushingClubKnockdown:
    return CrushingClubKnockdown(
        uses_crushing_club(attacker, selection) and struck and not slain
    )
