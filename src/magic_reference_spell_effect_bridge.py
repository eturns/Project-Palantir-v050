"""
Project Palantír
DEV-080-F4B: Reference Spell Effect Bridge.

Author: Edward Turns (Project Lead)

Reuses existing verified spell-effect functions
under explicitly supplied reference conditions.

No arbitrary spell weights or production scores.
"""

from dataclasses import dataclass
from fractions import Fraction

from magic_spell_impact_coverage import (
    VERIFIED_EFFECT_FUNCTIONS,
)


REQUIRED_CONTEXT = {
    "CHILL_SOUL": (
        "target_remaining_wounds",
        "conditional_wound_not_prevented_probability",
    ),
    "COMPEL": (
        "target_move_inches",
        "target_engaged_in_combat",
    ),
    "CURSE": (
        "target_remaining_fate",
        "target_part",
    ),
    "DRAIN_COURAGE": (
        "target_courage_required_roll",
        "target_part",
    ),
    "FOG_OF_DISARRAY": (),
    "INSTIL_FEAR": (),
    "TRANSFIX": (),
    "WITHER": (
        "target_current_strength",
        "target_part",
    ),
    "YOUR_STAFF_IS_BROKEN": (
        "target_has_staff_of_power",
    ),
}


@dataclass(frozen=True)
class MagicReferenceSpellEffect:
    spell_id: str
    effect_probability: Fraction
    mechanical_evidence: object
    evidence_status: str = (
        "verified_reference_spell_effect"
    )
    dashboard_score: None = None
    scenario_score: None = None


def evaluate_reference_spell_effect(
    *,
    spell_id: str,
    effect_probability: Fraction,
    context: dict,
) -> MagicReferenceSpellEffect:
    """
    Evaluate one spell using its existing
    rules-backed mechanical function.

    effect_probability must already incorporate
    relevant casting and resistance resolution.
    """

    if spell_id not in VERIFIED_EFFECT_FUNCTIONS:
        raise ValueError(
            f"No verified effect function: {spell_id}"
        )

    if not isinstance(effect_probability, Fraction):
        raise TypeError(
            "effect_probability must be Fraction"
        )

    if not 0 <= effect_probability <= 1:
        raise ValueError(
            "effect_probability outside [0, 1]"
        )

    if not isinstance(context, dict):
        raise TypeError("context must be dict")

    required = set(REQUIRED_CONTEXT[spell_id])
    supplied = set(context)

    missing = required - supplied
    unexpected = supplied - required

    if missing:
        raise ValueError(
            f"Missing reference context: {sorted(missing)}"
        )

    if unexpected:
        raise ValueError(
            f"Unexpected reference context: "
            f"{sorted(unexpected)}"
        )

    evaluator = VERIFIED_EFFECT_FUNCTIONS[spell_id]

    evidence = evaluator(
        effect_probability=effect_probability,
        **context,
    )

    return MagicReferenceSpellEffect(
        spell_id=spell_id,
        effect_probability=effect_probability,
        mechanical_evidence=evidence,
    )