"""
Project Palantír
DEV-080-F4: Quantitative Reference Spell Outcomes.

Author: Edward Turns (Project Lead)

Calculates reference-context outcomes in natural
mechanical units.

Does not combine damage and control into an
arbitrary scalar or alter production scoring.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MagicReferenceEffectOutcome:
    spell_id: str
    effect_probability: Fraction
    expected_wounds: Fraction | None
    expected_denied_activations: Fraction | None
    evidence_status: str
    dashboard_score: None = None
    scenario_score: None = None


def calculate_reference_chill_soul(
    *,
    effect_probability: Fraction,
    target_eligible: bool,
    wound_prevention_excluded: bool,
) -> MagicReferenceEffectOutcome:
    """
    One expected Wound per successful effect.

    The caller must supply the probability that
    the spell takes effect after relevant
    casting and resistance resolution.
    """
    _validate_probability(effect_probability)

    if type(target_eligible) is not bool:
        raise TypeError("target_eligible must be bool")

    if type(wound_prevention_excluded) is not bool:
        raise TypeError(
            "wound_prevention_excluded must be bool"
        )

    if not target_eligible or not wound_prevention_excluded:
        return MagicReferenceEffectOutcome(
            spell_id="CHILL_SOUL",
            effect_probability=effect_probability,
            expected_wounds=None,
            expected_denied_activations=None,
            evidence_status="reference_context_incomplete",
        )

    return MagicReferenceEffectOutcome(
        spell_id="CHILL_SOUL",
        effect_probability=effect_probability,
        expected_wounds=effect_probability,
        expected_denied_activations=None,
        evidence_status="conditional_wound_outcome",
    )


def calculate_reference_transfix(
    *,
    effect_probability: Fraction,
    target_eligible: bool,
    activation_remaining: bool,
) -> MagicReferenceEffectOutcome:
    """
    Model one denied activation when the target
    could otherwise still activate.

    Other restrictions remain separate evidence.
    """
    _validate_probability(effect_probability)

    if type(target_eligible) is not bool:
        raise TypeError("target_eligible must be bool")

    if type(activation_remaining) is not bool:
        raise TypeError(
            "activation_remaining must be bool"
        )

    if not target_eligible:
        return MagicReferenceEffectOutcome(
            spell_id="TRANSFIX",
            effect_probability=effect_probability,
            expected_wounds=None,
            expected_denied_activations=None,
            evidence_status="reference_context_incomplete",
        )

    return MagicReferenceEffectOutcome(
        spell_id="TRANSFIX",
        effect_probability=effect_probability,
        expected_wounds=None,
        expected_denied_activations=(
            effect_probability
            if activation_remaining
            else Fraction(0)
        ),
        evidence_status="conditional_activation_denial",
    )


def _validate_probability(value: Fraction) -> None:
    if not isinstance(value, Fraction):
        raise TypeError(
            "effect_probability must be a Fraction"
        )

    if not 0 <= value <= 1:
        raise ValueError(
            "effect_probability must be between 0 and 1"
        )