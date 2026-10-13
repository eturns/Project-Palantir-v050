"""DEV-077S-I2-F2-A1: diagnostic-only casting evidence.

This module does not change the legacy Magic score. A casting attempt is an
explicit hypothetical resource allocation, NOT an assumed turn or target.
Additional dice are identified separately from Will-funded dice. The caller
must validate the source, eligibility and timing of additional dice against
applicable rules; no Will refund/free-die rule is inferred here.

The base threshold calculation is the repository's existing 'at least one D6
meets the cast value' model. Spell-specific and 2024 casting exceptions are
NOT silently applied. Those require separate evidence in later checkpoints.
"""
from dataclasses import dataclass
from math import isfinite

from spell_probability import casting_probability


@dataclass(frozen=True)
class MagicCastEvidence:
    cast_value: int
    will_available: int
    will_spent: int
    additional_dice: int
    dice_total: int
    probability: float
    will_remaining_after_attempt: int
    extra_dice_source: str | None
    evidence_status: str = "diagnostic_not_calibrated"
    calculation_model: str = "one_or_more_d6_meet_threshold"
    dashboard_score: None = None
    scenario_score: None = None


def _integer(value: object, name: str, *, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{name} must be between {minimum} and {maximum}" if maximum is not None
                         else f"{name} must be at least {minimum}")
    return value


def calculate_cast_evidence(
    *,
    cast_value: int,
    will_available: int,
    will_spent: int,
    additional_dice: int = 0,
    extra_dice_source: str | None = None,
) -> MagicCastEvidence:
    """Compute one declared hypothetical casting allocation.

    At least one Will must be spent in this general-purpose model, matching
    spell_probability.casting_probability_with_resource_state. Do not use
    for free-cast exceptions without an explicit later rules-aware adapter.
    No cast frequency, opportunity, resistance or spell effect is modelled.
    """
    _integer(cast_value, "cast_value", minimum=1, maximum=6)
    _integer(will_available, "will_available", minimum=0)
    _integer(will_spent, "will_spent", minimum=1)
    _integer(additional_dice, "additional_dice", minimum=0)
    if will_spent > will_available:
        raise ValueError("will_spent cannot exceed will_available")
    if additional_dice and (not isinstance(extra_dice_source, str) or not extra_dice_source.strip()):
        raise ValueError("additional_dice require an explicit extra_dice_source")
    if extra_dice_source is not None and (not isinstance(extra_dice_source, str) or not extra_dice_source.strip()):
        raise ValueError("extra_dice_source must be non-blank when supplied")
    if not additional_dice and extra_dice_source is not None:
        raise ValueError("extra_dice_source requires additional_dice")
    dice_total = will_spent + additional_dice
    probability = casting_probability(cast_value=cast_value, dice_count=dice_total)
    if not isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("casting probability must be finite and within [0, 1]")
    return MagicCastEvidence(
        cast_value=cast_value,
        will_available=will_available,
        will_spent=will_spent,
        additional_dice=additional_dice,
        dice_total=dice_total,
        probability=probability,
        will_remaining_after_attempt=will_available - will_spent,
        extra_dice_source=extra_dice_source,
    )


def enumerate_cast_allocations(
    *,
    cast_value: int,
    will_available: int,
    additional_dice: int = 0,
    extra_dice_source: str | None = None,
) -> tuple[MagicCastEvidence, ...]:
    """All Will spends for ONE potential attempt; not expected spell frequency."""
    _integer(cast_value, "cast_value", minimum=1, maximum=6)
    _integer(will_available, "will_available", minimum=0)
    _integer(additional_dice, "additional_dice", minimum=0)
    if additional_dice and (not isinstance(extra_dice_source, str) or not extra_dice_source.strip()):
        raise ValueError("additional_dice require an explicit extra_dice_source")
    if not additional_dice and extra_dice_source is not None:
        raise ValueError("extra_dice_source requires additional_dice")
    return tuple(
        calculate_cast_evidence(
            cast_value=cast_value, will_available=will_available,
            will_spent=spent, additional_dice=additional_dice,
            extra_dice_source=extra_dice_source,
        )
        for spent in range(1, will_available + 1)
    )
