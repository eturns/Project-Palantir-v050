"""DEV-077S-I2-G2-D4B3: reusable, rules-backed nonlethal spell effects.

2024 MESBG Rules Manual, printed pages 117-120. These are conditional
outcomes AFTER a legal cast and unsuccessful resistance. Their probabilities
are supplied by the D1 diagnostic. They do not predict tactical advantage,
attribute suppression duration beyond the defined state, or elimination.
"""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class RemainingSpellEvidence:
    spell_id: str
    effect_probability: Fraction
    duration: str
    remaining_fate_on_effect: int | None = None
    courage_target_on_effect: int | None = None
    intelligence_test_modifier_on_effect: int | None = None
    intelligence_area_inches: int | None = None
    fearful_area_inches: int | None = None
    gains_fearful_on_effect: bool = False
    staff_destroyed_on_effect: bool = False
    direct_elimination_probability: Fraction = Fraction(0)
    evidence_status: str = "rules_verified_conditional_effect_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def _probability(p: Fraction) -> None:
    if not isinstance(p, Fraction) or not Fraction(0) <= p <= Fraction(1):
        raise ValueError("effect_probability must be a Fraction in [0, 1]")


def _nonnegative(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def calculate_curse_hero_hunting(*, effect_probability: Fraction,
                                 target_remaining_fate: int,
                                 target_part: str = "model") -> RemainingSpellEvidence:
    """Curse removes one Fate; zero Fate stays zero. Cavalry part explicit."""
    _probability(effect_probability)
    _nonnegative(target_remaining_fate, "target_remaining_fate")
    if target_part not in {"model", "rider", "mount"}:
        raise ValueError("Curse requires explicit model/rider/mount target part")
    return RemainingSpellEvidence(
        spell_id="CURSE", effect_probability=effect_probability, duration="instant",
        remaining_fate_on_effect=max(0, target_remaining_fate - 1),
        evidence_status="verified_target_part_fate_reduction_not_immediate_elimination",
    )


def calculate_drain_courage_hero_hunting(*, effect_probability: Fraction,
                                         target_courage_required_roll: int,
                                         target_part: str = "model") -> RemainingSpellEvidence:
    """Drain Courage worsens Courage by one, cumulatively; maximum 7+."""
    _probability(effect_probability)
    if type(target_courage_required_roll) is not int or not 2 <= target_courage_required_roll <= 7:
        raise ValueError("Courage required roll must be 2..7")
    if target_part not in {"model", "rider", "mount"}:
        raise ValueError("Drain Courage requires explicit model/rider/mount target part")
    return RemainingSpellEvidence(
        spell_id="DRAIN_COURAGE", effect_probability=effect_probability,
        duration="persistent_remainder_of_game",
        courage_target_on_effect=min(7, target_courage_required_roll + 1),
    )


def calculate_fog_of_disarray_hero_hunting(*, effect_probability: Fraction) -> RemainingSpellEvidence:
    """Self-targeted Exhaustion; enemy Intelligence Tests within 6 inches -1."""
    _probability(effect_probability)
    return RemainingSpellEvidence(
        spell_id="FOG_OF_DISARRAY", effect_probability=effect_probability,
        duration="exhaustion", intelligence_test_modifier_on_effect=-1,
        intelligence_area_inches=6,
        evidence_status="verified_area_effect_requires_caster_position_and_duration_state",
    )


def calculate_instil_fear_hero_hunting(*, effect_probability: Fraction) -> RemainingSpellEvidence:
    """Self-targeted Temporary; enemies within 6 inches become Fearful."""
    _probability(effect_probability)
    return RemainingSpellEvidence(
        spell_id="INSTIL_FEAR", effect_probability=effect_probability,
        duration="temporary_until_end_phase", fearful_area_inches=6,
        gains_fearful_on_effect=True,
        evidence_status="verified_area_effect_requires_caster_position",
    )


def calculate_your_staff_is_broken_hero_hunting(*, effect_probability: Fraction,
                                                target_has_staff_of_power: bool) -> RemainingSpellEvidence:
    """Destroys a target Staff of Power; no direct damage or elimination."""
    _probability(effect_probability)
    if type(target_has_staff_of_power) is not bool:
        raise ValueError("target_has_staff_of_power must be bool")
    if not target_has_staff_of_power:
        raise ValueError("Incomplete Hero Hunting: target does not have a Staff of Power")
    return RemainingSpellEvidence(
        spell_id="YOUR_STAFF_IS_BROKEN", effect_probability=effect_probability,
        duration="instant", staff_destroyed_on_effect=True,
        evidence_status="verified_staff_removal_future_impact_not_calibrated",
    )
