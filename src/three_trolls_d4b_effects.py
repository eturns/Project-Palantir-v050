"""DEV-077-TT-D4B: three purchased Three Trolls upgrades (2024 Hobbit p.158).

Pure, opt-in evidence. Does not mutate models, roll dice, or alter calibrated
scores. Requires validated HoardEvidence; never treats a listed rule as bought.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from three_trolls_campfire import CampfireEffects, evaluate_campfire_effects
from three_trolls_d4a_effects import _ensure_hoard, _ensure_troll
from three_trolls_hoard import HoardEvidence

STONE_RANGE_INCHES = 12
STONE_STRENGTH = 8
CAMPFIRE_BASE_RANGE_INCHES = 6
CAMPFIRE_UPGRADED_RANGE_INCHES = 18


@dataclass(frozen=True)
class WarmFireEvidence:
    upgraded: bool
    campfire_range_inches: float
    proximity: CampfireEffects
    endgame_banner_vp: bool | None
    endgame_status: str


def nothing_like_a_warm_fire(
    hoard: HoardEvidence,
    profile_id: str,
    *,
    campfire_placed: bool | None = None,
    distance_inches: float | None = None,
    end_of_game: bool | None = None,
    enemy_in_base_contact: bool | None = None,
    scenario_awards_surviving_banner_vp: bool | None = None,
) -> WarmFireEvidence:
    """18in proximity if bought, plus conditional end-game banner VP effect.

    The base Campfire banner proximity applies regardless of upgrade.
    This function evaluates ONLY the additional scenario VP rule when bought.
    """
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    for field, value in (
        ("end_of_game", end_of_game),
        ("enemy_in_base_contact", enemy_in_base_contact),
        ("scenario_awards_surviving_banner_vp", scenario_awards_surviving_banner_vp),
    ):
        if value is not None and type(value) is not bool:
            raise TypeError(f"{field} must be bool or None")
    if campfire_placed is False and enemy_in_base_contact is True:
        raise ValueError("An unplaced Campfire cannot have an enemy in base contact")
    upgraded = hoard.has("Nothing like a warm fire")
    radius = CAMPFIRE_UPGRADED_RANGE_INCHES if upgraded else CAMPFIRE_BASE_RANGE_INCHES
    proximity = evaluate_campfire_effects(
        profile_id, campfire_placed=campfire_placed,
        distance_inches=distance_inches, range_inches=radius,
    )
    if not upgraded:
        return WarmFireEvidence(False, radius, proximity, False, "not_purchased")
    if end_of_game is False:
        return WarmFireEvidence(True, radius, proximity, None, "not_endgame")
    if end_of_game is None:
        return WarmFireEvidence(True, radius, proximity, None, "conditional_not_evaluated")
    if scenario_awards_surviving_banner_vp is False:
        return WarmFireEvidence(True, radius, proximity, False, "evaluated")
    if campfire_placed is False:
        return WarmFireEvidence(True, radius, proximity, False, "evaluated")
    if enemy_in_base_contact is True:
        return WarmFireEvidence(True, radius, proximity, False, "evaluated")
    if (scenario_awards_surviving_banner_vp is None
            or campfire_placed is None or enemy_in_base_contact is None):
        return WarmFireEvidence(True, radius, proximity, None, "conditional_not_evaluated")
    return WarmFireEvidence(True, radius, proximity, True, "evaluated")


@dataclass(frozen=True)
class BowlThemOverEvidence:
    upgraded: bool
    throwing_weapon_available: bool
    throwing_weapon_strength: int | None
    throwing_weapon_range_inches: int | None
    hurl_distance_reroll_allowed: bool
    hurl_first_roll: int | None
    hurl_second_roll: int | None
    chosen_hurl_distance_roll: int | None
    status: str


def bowl_them_over(
    hoard: HoardEvidence, profile_id: str, *,
    used_hurl: bool | None = None,
    hurl_first_roll: int | None = None,
    hurl_second_roll: int | None = None,
    choose_reroll: bool | None = None,
) -> BowlThemOverEvidence:
    """Throwing stones are S8, 12in; Hurl distance die may be rerolled.

    No dice rolled here. A reroll replaces the first result even when worse,
    and a second reroll is never permitted.
    """
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if used_hurl is not None and type(used_hurl) is not bool:
        raise TypeError("used_hurl must be bool or None")
    if choose_reroll is not None and type(choose_reroll) is not bool:
        raise TypeError("choose_reroll must be bool or None")
    for label, roll in (("hurl_first_roll", hurl_first_roll), ("hurl_second_roll", hurl_second_roll)):
        if roll is not None and (type(roll) is not int or not 1 <= roll <= 6):
            raise ValueError(f"{label} requires a natural D6 roll")
    if hurl_first_roll is not None and used_hurl is not True:
        raise ValueError("Hurl dice require a Hurl action")
    if hurl_second_roll is not None and (hurl_first_roll is None or choose_reroll is not True):
        raise ValueError("Second roll requires choosing a reroll of a first roll")
    if choose_reroll is True and (used_hurl is not True or hurl_first_roll is None):
        raise ValueError("A reroll requires an actual Hurl distance roll")
    active = hoard.has("Bowl them over")
    if not active and (choose_reroll is True or hurl_second_roll is not None):
        raise ValueError("Cannot use unpurchased Hurl reroll")
    selected = hurl_second_roll if choose_reroll and hurl_second_roll is not None else (
        hurl_first_roll if choose_reroll is not True else None
    )
    status = "evaluated"
    if used_hurl is True and choose_reroll is True and hurl_second_roll is None:
        status = "conditional_not_evaluated"
    return BowlThemOverEvidence(
        upgraded=active,
        throwing_weapon_available=active,
        throwing_weapon_strength=STONE_STRENGTH if active else None,
        throwing_weapon_range_inches=STONE_RANGE_INCHES if active else None,
        hurl_distance_reroll_allowed=active,
        hurl_first_roll=hurl_first_roll,
        hurl_second_roll=hurl_second_roll,
        chosen_hurl_distance_roll=selected,
        status=status,
    )


@dataclass(frozen=True)
class KitchenUtensilsEvidence:
    upgraded: bool
    is_strike: bool | None
    original_natural_roll: int | None
    reroll_allowed: bool
    reroll_natural_roll: int | None
    effective_natural_roll: int | None
    status: str
    chance_to_wound_on_single_roll: Fraction | None
    chance_to_wound_with_reroll: Fraction | None


def kitchen_utensils(
    hoard: HoardEvidence, profile_id: str, *,
    is_strike: bool | None = None,
    original_natural_roll: int | None = None,
    reroll_natural_roll: int | None = None,
    wound_target: int | None = None,
) -> KitchenUtensilsEvidence:
    """Re-roll a natural one to wound when making Strikes, only if bought.

    Optional probability uses a single D6 To Wound target (2..6); complex
    6/4+ and other multi-die wound mechanics are deliberately unevaluated.
    """
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if is_strike is not None and type(is_strike) is not bool:
        raise TypeError("is_strike must be bool or None")
    for label, roll in (("original_natural_roll", original_natural_roll),
                        ("reroll_natural_roll", reroll_natural_roll)):
        if roll is not None and (type(roll) is not int or not 1 <= roll <= 6):
            raise ValueError(f"{label} must be an integer from 1 to 6")
    if wound_target is not None and (type(wound_target) is not int or not 2 <= wound_target <= 6):
        raise ValueError("wound_target must be a simple D6 target of 2 through 6")
    if original_natural_roll is not None and is_strike is not True:
        raise ValueError("To Wound rolls require Strikes")
    active = hoard.has("Kitchen Utensils")
    eligible = active and is_strike is True and original_natural_roll == 1
    if reroll_natural_roll is not None and not eligible:
        raise ValueError("Wound reroll requires purchased upgrade and a natural 1 on a Strike")
    simple_chance = Fraction(7 - wound_target, 6) if wound_target is not None else None
    upgraded_chance = (
        simple_chance + Fraction(1, 6) * simple_chance
        if active and simple_chance is not None else simple_chance
    )
    effective = (reroll_natural_roll if reroll_natural_roll is not None
                 else original_natural_roll if not eligible else None)
    status = ("conditional_not_evaluated" if is_strike is None
              or eligible and reroll_natural_roll is None else "evaluated")
    return KitchenUtensilsEvidence(
        active, is_strike, original_natural_roll, eligible,
        reroll_natural_roll, effective, status, simple_chance, upgraded_chance,
    )
