
"""
Project Palantír
DEV-080-B1: Magic capability measurement foundation.

Author: Edward Turns (Project Lead)

Diagnostic only. Does not alter scoring, scenarios,
optimisation or frozen calibration.
"""

from dataclasses import dataclass

from mechanical_magic_spell_profiles import (
    ProfileMagicCastingEvidence,
)
from mechanical_magic_casting import MagicCastEvidence


@dataclass(frozen=True)
class MagicCapabilityMeasurement:
    profile_id: str
    spell_id: str
    cast_value: int
    starting_will: int
    will_spent: int
    additional_dice: int
    casting_probability: float
    remaining_will: int
    conditional_rule_ids: tuple[str, ...]
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def measure_magic_casting_potential(
    evidence: ProfileMagicCastingEvidence,
    *,
    spell_id: str,
    will_spent: int = 1,
    verified_rule_ids: tuple[str, ...] = (),
) -> MagicCapabilityMeasurement:
    """
    Measure one hypothetical casting attempt.

    Does not assume a legal target, actual opportunity,
    successful spell effect or enemy resistance.
    """
    if not isinstance(evidence, ProfileMagicCastingEvidence):
        raise TypeError(
            "Expected ProfileMagicCastingEvidence"
        )

    if not isinstance(spell_id, str) or not spell_id:
        raise ValueError("spell_id must be nonblank")

    if isinstance(will_spent, bool) or not isinstance(
        will_spent, int
    ) or will_spent < 1:
        raise ValueError("will_spent must be a positive integer")

    if not isinstance(verified_rule_ids, tuple) or any(
        not isinstance(rule, str) or not rule
        for rule in verified_rule_ids
    ):
        raise TypeError(
            "verified_rule_ids must be a tuple of rule IDs"
        )

    candidates = [
        option
        for option in evidence.spell_options
        if option.spell_id == spell_id
        and set(option.conditional_rule_ids).issubset(
            verified_rule_ids
        )
    ]

    if not candidates:
        raise ValueError(
            "Spell unavailable under verified conditions"
        )

    # Prefer the most specifically verified option.
    option = max(
        candidates,
        key=lambda item: len(item.conditional_rule_ids),
    )

    allocation: MagicCastEvidence | None = next(
        (
            item
            for item in option.allocations
            if item.will_spent == will_spent
        ),
        None,
    )

    if allocation is None:
        raise ValueError(
            "Requested Will allocation is unavailable"
        )

    return MagicCapabilityMeasurement(
        profile_id=evidence.profile_id,
        spell_id=option.spell_id,
        cast_value=option.cast_value,
        starting_will=evidence.will_available,
        will_spent=allocation.will_spent,
        additional_dice=allocation.additional_dice,
        casting_probability=allocation.probability,
        remaining_will=allocation.will_remaining_after_attempt,
        conditional_rule_ids=option.conditional_rule_ids,
    )