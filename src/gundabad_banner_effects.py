"""DEV-078-AoG-E2: Raise the Banners three mechanical effects.

Author: Edward Turns (Project Lead).
Reads immutable E1 BannerState; no scoring or battlefield inference.
"""
from dataclasses import dataclass
from fractions import Fraction

from combat_side import CombatSide
from gundabad_raise_the_banners import Banner, BannerState, is_banner_active
from oblivious_to_pain import prevention_probability as ordinary_oblivious_probability

BERSERKER_ID = "GUNDABAD_BERSERKER"


def _profile(combatant):
    """Accept a Profile or a ConfiguredProfile, without making roster assumptions."""
    profile = getattr(combatant, "profile", combatant)
    if not hasattr(profile, "id") or not hasattr(profile, "factions"):
        raise TypeError("Profile or ConfiguredProfile required")
    return profile


def _eligible(state: BannerState, banner: Banner, combatant) -> bool:
    profile = _profile(combatant)
    return is_banner_active(state, banner) and "GUNDABAD" in profile.factions


def banner_reroll_eligible(state: BannerState, combatant) -> bool:
    """Dol Guldur: the friendly Gundabad model counts as within banner range.

    Caller must supply a friendly model; this is not an opponent identity resolver.
    """
    return _eligible(state, Banner.DOL_GULDUR, combatant)


def with_dol_guldur_banner_support(
    side: CombatSide, *, state: BannerState, friendly_combatants: tuple
) -> CombatSide:
    """Reuse CombatSide's standard reroll_available flag.

    Combat composition and friendly-vs-enemy ownership are caller supplied.
    """
    if not isinstance(side, CombatSide):
        raise TypeError("CombatSide required")
    if not isinstance(friendly_combatants, tuple) or not friendly_combatants:
        raise ValueError("Nonempty tuple of friendly combatants required")
    eligible = any(banner_reroll_eligible(state, c) for c in friendly_combatants)
    if not eligible:
        return side
    from dataclasses import replace
    return replace(side, reroll_available=True)


def free_heroic_march_eligible(state: BannerState, combatant) -> bool:
    """Gundabad: friendly Gundabad Heroes may declare Heroic March for free.

    This is cost entitlement, not a grant of an unavailable Heroic Action.
    """
    profile = _profile(combatant)
    status = getattr(profile, "heroic_status", None)
    return (_eligible(state, Banner.GUNDABAD, combatant)
            and getattr(status, "value", status) == "HERO")


@dataclass(frozen=True)
class HeroicMarchCost:
    eligible_for_free_march: bool
    might_cost: int
    action_availability_verified: bool = False


def heroic_march_cost(state: BannerState, combatant, *, can_declare_heroic_march: bool,
                      base_might_cost: int = 1) -> HeroicMarchCost:
    if type(can_declare_heroic_march) is not bool:
        raise TypeError("Action availability must be a verified bool")
    if type(base_might_cost) is not int or base_might_cost < 0:
        raise ValueError("Might cost must be a nonnegative integer")
    eligible = can_declare_heroic_march and free_heroic_march_eligible(state,combatant)
    return HeroicMarchCost(eligible, 0 if eligible else base_might_cost, True)


def angmar_prevention_probability(state: BannerState, combatant) -> Fraction:
    """One post-wound prevention roll; Berserker 5+ replaces Oblivious 6+.

    No parallel 6+ roll is added when Oblivious to Pain applies.
    """
    profile = _profile(combatant)
    ordinary = ordinary_oblivious_probability(combatant)
    if not _eligible(state, Banner.ANGMAR, combatant):
        return ordinary
    if profile.id == BERSERKER_ID and ordinary:
        return Fraction(1, 3)  # Natural 5+ replaces normal 6+
    # The banner grants a 6+ roll to qualifying models. If another
    # prevention rule exists, this adapter does not stack separate rolls.
    return max(ordinary, Fraction(1, 6))


def resolve_angmar_prevention(state: BannerState, combatant, natural_d6: int) -> bool:
    if type(natural_d6) is not int or not 1 <= natural_d6 <= 6:
        raise ValueError("Natural prevention roll must be D6 (1..6)")
    probability = angmar_prevention_probability(state, combatant)
    return probability > 0 and natural_d6 >= (7 - int(probability*6))
