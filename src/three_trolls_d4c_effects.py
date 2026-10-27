"""DEV-077-TT-D4C: conditional, purchase-gated Three Trolls effects.

Rules: MESBG Armies of the Hobbit (2024), Three Trolls, p.158.
Pure diagnostic resolvers. No battlefield state or calibrated score is mutated.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from three_trolls_d4a_effects import _ensure_hoard, _ensure_troll
from three_trolls_hoard import HoardEvidence


def _optional_bool(name: str, value: bool | None) -> None:
    if value is not None and type(value) is not bool:
        raise TypeError(f'{name} must be bool or None')


@dataclass(frozen=True)
class DominantPresenceEvidence:
    purchased: bool
    within_three_inches: bool | None
    opponent_equivalent_in_range: bool | None
    automatically_controls_objective: bool | None
    opponents_treated_as_out_of_range: bool | None
    status: str


def dominant_presence(
    hoard: HoardEvidence, profile_id: str, *,
    distance_to_objective_inches: float | None = None,
    opponent_equivalent_in_range: bool | None = None,
) -> DominantPresenceEvidence:
    """Equivalent opposing effects within range cancel each other.

    No claim about ordinary objective control when the upgrade is absent,
    beyond 3", or when opposing equivalent-rule presence is unknown.
    """
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    _optional_bool('opponent_equivalent_in_range', opponent_equivalent_in_range)
    if distance_to_objective_inches is not None:
        if isinstance(distance_to_objective_inches, bool) or not isinstance(distance_to_objective_inches, (int, float)):
            raise TypeError('Objective distance must be a number or None')
        if not 0 <= distance_to_objective_inches < float('inf'):
            raise ValueError('Objective distance must be finite and non-negative')
    bought = hoard.has('Dominant presence')
    near = None if distance_to_objective_inches is None else distance_to_objective_inches <= 3
    if not bought:
        return DominantPresenceEvidence(False, near, opponent_equivalent_in_range, False, False, 'not_purchased')
    if near is False:
        return DominantPresenceEvidence(True, False, opponent_equivalent_in_range, False, False, 'evaluated')
    if near is None or opponent_equivalent_in_range is None:
        return DominantPresenceEvidence(True, near, opponent_equivalent_in_range, None, None, 'conditional_not_evaluated')
    active = not opponent_equivalent_in_range
    return DominantPresenceEvidence(True, near, opponent_equivalent_in_range, active, active, 'evaluated')


@dataclass(frozen=True)
class SavvyFightersEvidence:
    purchased: bool
    gains_heroic_strike: bool
    enemy_declared_heroic_strike: bool | None
    same_combat: bool | None
    natural_roll: int | None
    may_declare_free_heroic_strike: bool | None
    chance_given_eligible_trigger: Fraction
    status: str


def savvy_fighters(
    hoard: HoardEvidence, profile_id: str, *,
    already_has_heroic_strike: bool = False,
    enemy_declared_heroic_strike: bool | None = None,
    same_combat: bool | None = None,
    natural_roll: int | None = None,
) -> SavvyFightersEvidence:
    """On 4+ a Troll in the same fight may declare a free Heroic Strike.

    This only grants permission; it does not spend Might or assume declaration.
    """
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    for name, value in (('already_has_heroic_strike', already_has_heroic_strike),
                        ('enemy_declared_heroic_strike', enemy_declared_heroic_strike),
                        ('same_combat', same_combat)):
        _optional_bool(name, value)
    if natural_roll is not None and (type(natural_roll) is not int or not 1 <= natural_roll <= 6):
        raise ValueError('Heroic Strike reaction requires a natural D6 roll')
    bought = hoard.has('Savvy Fighters')
    eligible = enemy_declared_heroic_strike is True and same_combat is True
    if natural_roll is not None and (not bought or not eligible):
        raise ValueError('Reaction roll requires purchased upgrade and enemy Heroic Strike in same combat')
    if not bought:
        free, status = False, 'not_purchased'
    elif enemy_declared_heroic_strike is False or same_combat is False:
        free, status = False, 'evaluated'
    elif enemy_declared_heroic_strike is None or same_combat is None or natural_roll is None:
        free, status = None, 'conditional_not_evaluated'
    else:
        free, status = natural_roll >= 4, 'evaluated'
    return SavvyFightersEvidence(bought, bought and not already_has_heroic_strike,
                                  enemy_declared_heroic_strike, same_combat, natural_roll,
                                  free, Fraction(1, 2) if bought else Fraction(0), status)


@dataclass(frozen=True)
class TrollCunningEvidence:
    purchased: bool
    standing: bool | None
    can_be_trapped: bool | None
    making_strikes: bool | None
    target_trapped: bool | None
    failed_to_wound_roll: bool | None
    may_reroll_failed_wound: bool | None
    status: str


def troll_cunning(
    hoard: HoardEvidence, profile_id: str, *,
    standing: bool | None = None,
    making_strikes: bool | None = None,
    target_trapped: bool | None = None,
    failed_to_wound_roll: bool | None = None,
) -> TrollCunningEvidence:
    """Standing Troll cannot be Trapped; failed Strike wounds vs Trapped reroll.

    Reroll does not apply to alternative attacks or successful wound rolls.
    The rerolled die result is deliberately resolved by the wound engine.
    """
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    for name, value in (('standing', standing), ('making_strikes', making_strikes),
                        ('target_trapped', target_trapped), ('failed_to_wound_roll', failed_to_wound_roll)):
        _optional_bool(name, value)
    bought = hoard.has('Troll Cunning')
    can_be_trapped = None if standing is None else not (bought and standing)
    if not bought:
        return TrollCunningEvidence(False, standing, can_be_trapped, making_strikes,
                                    target_trapped, failed_to_wound_roll, False, 'not_purchased')
    if making_strikes is False or target_trapped is False or failed_to_wound_roll is False:
        reroll = False
    elif making_strikes is True and target_trapped is True and failed_to_wound_roll is True:
        reroll = True
    else:
        reroll = None
    return TrollCunningEvidence(True, standing, can_be_trapped, making_strikes,
                                target_trapped, failed_to_wound_roll, reroll,
                                'evaluated' if standing is not None and reroll is not None
                                else 'conditional_not_evaluated')
