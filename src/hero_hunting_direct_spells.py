"""DEV-077S-I2-G2-D4B1: rules-backed Chill Soul and Wither outcomes.

Sources: 2024 MESBG Rules Manual, printed pages 117 (Chill Soul)
 and 120 (Wither); Necromancer spell profile in Armies of the Hobbit.

The supplied effect_probability comes from the D1 cast/resist diagnostic.
Target access and casting resources must already have been verified.
No scoring or implicit modelling of Fate/Will-as-Fate/other prevention.
"""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DirectSpellHeroHuntingEvidence:
    spell_id: str
    effect_probability: Fraction
    target_elimination_probability: Fraction | None
    conditional_wounds: int
    resulting_strength: int | None
    evidence_status: str
    dashboard_score: None = None
    scenario_score: None = None


def _probability(value: Fraction, name: str) -> None:
    if not isinstance(value, Fraction) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be a Fraction in [0, 1]")


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def calculate_chill_soul_hero_hunting(
    *,
    effect_probability: Fraction,
    target_remaining_wounds: int,
    conditional_wound_not_prevented_probability: Fraction | None = None,
) -> DirectSpellHeroHuntingEvidence:
    """Chill Soul causes one Wound; it is not a Strength-based hit.

    No elimination estimate is returned until prevention has been resolved.
    For one-Wound targets, the caller may supply a separately verified chance
    the Wound is not prevented (Fate and other defences included). For a target
    with more than one Wound, one successful spell cannot itself eliminate it.
    """
    _probability(effect_probability, "effect_probability")
    _positive_int(target_remaining_wounds, "target_remaining_wounds")
    if conditional_wound_not_prevented_probability is not None:
        _probability(
            conditional_wound_not_prevented_probability,
            "conditional_wound_not_prevented_probability",
        )
    if target_remaining_wounds > 1:
        elimination = Fraction(0)
        status = "verified_one_wound_nonlethal_in_declared_context"
    elif conditional_wound_not_prevented_probability is None:
        elimination = None
        status = "defensive_prevention_unresolved"
    else:
        elimination = (
            effect_probability * conditional_wound_not_prevented_probability
        )
        status = "conditional_prevention_probability_supplied"
    return DirectSpellHeroHuntingEvidence(
        spell_id="CHILL_SOUL",
        effect_probability=effect_probability,
        target_elimination_probability=elimination,
        conditional_wounds=1,
        resulting_strength=None,
        evidence_status=status,
    )


def calculate_wither_hero_hunting(
    *, effect_probability: Fraction, target_current_strength: int,
    target_part: str = "model",
) -> DirectSpellHeroHuntingEvidence:
    """Wither reduces the chosen target's Strength by one, to minimum zero.

    If zero, the chosen target is slain. For cavalry the chosen target part
    must be independently resolved; this API refuses unclear cavalry state.
    """
    _probability(effect_probability, "effect_probability")
    _positive_int(target_current_strength, "target_current_strength")
    if target_part not in ("model", "rider", "mount"):
        raise ValueError("Wither requires an explicit model/rider/mount target part")
    result = target_current_strength - 1
    return DirectSpellHeroHuntingEvidence(
        spell_id="WITHER",
        effect_probability=effect_probability,
        target_elimination_probability=(
            None if target_part == "mount" else
            effect_probability if result == 0 else Fraction(0)
        ),
        conditional_wounds=0,
        resulting_strength=result,
        evidence_status=(
            "chosen_part_eliminated_not_necessarily_hero"
            if target_part == "mount" and result == 0
            else "verified_strength_zero_elimination"
            if result == 0 else "verified_persistent_strength_reduction"
        ),
    )
