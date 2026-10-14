"""DEV-077S-I2-G2-D4B2: rules-backed Transfix/Compel diagnostic effects.

MESBG Rules Manual (2024), printed pp. 117 (Compel) and 119 (Transfix).
The spell has already taken effect: cast/resist success and legal targeting
are supplied by other modules. No elimination or dashboard score is inferred.
"""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ControlSpellEvidence:
    spell_id: str
    effect_probability: Fraction
    duration: str
    activation_blocked: bool
    shooting_blocked: bool
    heroic_actions_blocked: bool
    active_abilities_blocked: bool
    strikes_when_winning_duel_blocked: bool
    compelled_max_movement_inches: Fraction | None
    further_movement_blocked: bool
    direct_elimination_probability: None = None
    evidence_status: str = "verified_conditional_control_effect"
    dashboard_score: None = None
    scenario_score: None = None


def _probability(value: Fraction) -> None:
    if not isinstance(value, Fraction) or not 0 <= value <= 1:
        raise ValueError("effect_probability must be Fraction in [0, 1]")


def calculate_transfix_hero_hunting(*, effect_probability: Fraction) -> ControlSpellEvidence:
    """Transfix: restrictions until End Phase, conditional on effect success."""
    _probability(effect_probability)
    return ControlSpellEvidence(
        spell_id="TRANSFIX", effect_probability=effect_probability,
        duration="temporary_until_end_phase", activation_blocked=True,
        shooting_blocked=True, heroic_actions_blocked=True,
        active_abilities_blocked=True, strikes_when_winning_duel_blocked=True,
        compelled_max_movement_inches=None, further_movement_blocked=False,
    )


def calculate_compel_hero_hunting(
    *, effect_probability: Fraction, target_move_inches: int | Fraction,
    target_engaged_in_combat: bool = False,
) -> ControlSpellEvidence:
    """Compel: choose movement up to half Move, then no further movement.

    A model engaged in Combat cannot be moved out of Combat by Compel.
    Other movement constraints (terrain, Charge, obstacles, Ring, objects)
    remain external and must be resolved before predicting a final position.
    """
    _probability(effect_probability)
    if isinstance(target_move_inches, bool) or not isinstance(target_move_inches, (int, Fraction)):
        raise ValueError("target_move_inches must be a non-negative integer or Fraction")
    if target_move_inches < 0:
        raise ValueError("target_move_inches cannot be negative")
    if not isinstance(target_engaged_in_combat, bool):
        raise ValueError("target_engaged_in_combat must be bool")
    return ControlSpellEvidence(
        spell_id="COMPEL", effect_probability=effect_probability,
        duration="instant_with_movement_restriction_until_turn_end",
        activation_blocked=False, shooting_blocked=False,
        heroic_actions_blocked=False, active_abilities_blocked=False,
        strikes_when_winning_duel_blocked=False,
        compelled_max_movement_inches=(
            Fraction(0) if target_engaged_in_combat else Fraction(target_move_inches) / 2
        ),
        further_movement_blocked=not target_engaged_in_combat,
        evidence_status=("engaged_target_cannot_be_moved_out_of_combat"
                         if target_engaged_in_combat else "verified_compelled_movement_ceiling"),
    )
