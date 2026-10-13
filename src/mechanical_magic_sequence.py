"""DEV-077S-I2-F2-A4: diagnostic-only hypothetical casting sequence.

A caller supplies the allowed number of casting slots for an explicitly
hypothetical window. Army-rule eligibility, targets, resistance and timing
are not inferred. Every attempt spends Will, independent of its success.
"""
from dataclasses import dataclass
from math import fsum

from mechanical_magic_casting import MagicCastEvidence, calculate_cast_evidence
from mechanical_magic_spell_profiles import (
    ProfileMagicCastingEvidence,
    SpellCastingOptions,
)


@dataclass(frozen=True)
class PlannedMagicCast:
    spell_option: SpellCastingOptions
    will_to_spend: int
    conditional_rules_verified: bool = False


@dataclass(frozen=True)
class MagicCastingSequenceEvidence:
    profile_id: str
    starting_will: int
    remaining_will: int
    spent_will: int
    permitted_cast_slots: int
    attempts: tuple[MagicCastEvidence, ...]
    spell_ids: tuple[str, ...]
    expected_successes: float
    assumptions: tuple[str, ...] = (
        "Declared hypothetical casting window and externally supplied slot limit",
        "Spells and Will allocation explicitly selected by caller",
        "Roll probabilities use the existing threshold model; no resistance or spell effects",
        "All attempted spells spend Will regardless of casting success",
        "No target, range, cooldown, per-spell limit or army-rule eligibility inferred",
    )
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def _int(value: object, label: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer")
    if value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def calculate_magic_casting_sequence(
    profile_evidence: ProfileMagicCastingEvidence,
    planned_casts: tuple[PlannedMagicCast, ...],
    *,
    permitted_cast_slots: int,
) -> MagicCastingSequenceEvidence:
    """Evaluate one explicit, ordered plan without modifying scoring.

    A slot count is input evidence supplied by the caller, NOT calculated from
    the Necromancer (or another army) rule. An empty sequence is permitted.
    Spell-specific legality remains the responsibility of the future adapter.
    """
    if not isinstance(profile_evidence, ProfileMagicCastingEvidence):
        raise TypeError("profile_evidence must be ProfileMagicCastingEvidence")
    if not isinstance(planned_casts, tuple) or not all(
        isinstance(cast, PlannedMagicCast) for cast in planned_casts
    ):
        raise TypeError("planned_casts must be a tuple of PlannedMagicCast")
    _int(permitted_cast_slots, "permitted_cast_slots", 0)
    if len(planned_casts) > permitted_cast_slots:
        raise ValueError("planned casts exceed permitted_cast_slots")

    will = profile_evidence.will_available
    attempts = []
    spell_ids = []
    for planned in planned_casts:
        if not any(planned.spell_option is option for option in profile_evidence.spell_options):
            raise ValueError("spell option does not belong to profile evidence")
        _int(planned.will_to_spend, "will_to_spend", 1)
        if not isinstance(planned.conditional_rules_verified, bool):
            raise TypeError("conditional_rules_verified must be bool")
        option = planned.spell_option
        if option.conditional_rule_ids and not planned.conditional_rules_verified:
            raise ValueError("conditional casting rule requires verification")
        if planned.will_to_spend > will:
            raise ValueError("insufficient remaining Will for planned cast")
        # Existing F2-A2 allocations are the single source of the declared
        # additional-dice modifiers for a given spell option.
        allocation = next((a for a in option.allocations
                           if a.will_spent == planned.will_to_spend), None)
        if allocation is None:
            raise ValueError("planned Will allocation is unavailable for spell")
        attempt = calculate_cast_evidence(
            cast_value=option.cast_value,
            will_available=will,
            will_spent=planned.will_to_spend,
            additional_dice=allocation.additional_dice,
            extra_dice_source=allocation.extra_dice_source,
        )
        attempts.append(attempt)
        spell_ids.append(option.spell_id)
        will = attempt.will_remaining_after_attempt
    return MagicCastingSequenceEvidence(
        profile_id=profile_evidence.profile_id,
        starting_will=profile_evidence.will_available,
        remaining_will=will,
        spent_will=profile_evidence.will_available - will,
        permitted_cast_slots=permitted_cast_slots,
        attempts=tuple(attempts),
        spell_ids=tuple(spell_ids),
        expected_successes=fsum(a.probability for a in attempts),
    )
