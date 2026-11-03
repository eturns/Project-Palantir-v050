
"""
Project Palantír
DEV-080-C1: Magical Endurance assessment.

Author: Edward Turns (Project Lead)

Diagnostic-only assessment of one selected spell
in an explicitly hypothetical casting window.

No assumed battlefield targets, opportunities,
resistance, or resolved spell effects.
"""

from dataclasses import dataclass

from mechanical_magic_endurance import (
    calculate_magic_endurance,
)
from mechanical_magic_spell_profiles import (
    ProfileMagicCastingEvidence,
)


@dataclass(frozen=True)
class MagicalEnduranceAssessment:
    profile_id: str
    spell_id: str
    starting_will: int
    hypothetical_opportunities: int
    affordable_attempts: int
    modelled_attempts: int
    will_spent: int
    remaining_will: int
    probability_per_attempt: float
    expected_successful_casts: float
    applied_rule_ids: tuple[str, ...]

    evidence_status: str = "hypothetical_endurance_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def assess_spell_endurance(
    evidence: ProfileMagicCastingEvidence,
    *,
    spell_id: str,
    hypothetical_opportunities: int = 6,
    verified_rule_ids: tuple[str, ...] = (),
) -> MagicalEnduranceAssessment:
    """
    Assess repeated hypothetical attempts of one spell.

    One Will is spent per attempt. Conditional
    casting bonuses require explicitly verified rules.
    """
    if not isinstance(evidence, ProfileMagicCastingEvidence):
        raise TypeError(
            "Expected ProfileMagicCastingEvidence"
        )

    if not isinstance(spell_id, str) or not spell_id:
        raise ValueError("spell_id must be nonblank")

    if (
        isinstance(hypothetical_opportunities, bool)
        or not isinstance(hypothetical_opportunities, int)
        or hypothetical_opportunities < 0
    ):
        raise ValueError(
            "hypothetical_opportunities must be nonnegative"
        )

    if not isinstance(verified_rule_ids, tuple) or any(
        not isinstance(rule, str) or not rule
        for rule in verified_rule_ids
    ):
        raise TypeError(
            "verified_rule_ids must be a tuple of rule IDs"
        )

    options = [
        option
        for option in evidence.spell_options
        if option.spell_id == spell_id
        and set(option.conditional_rule_ids).issubset(
            verified_rule_ids
        )
    ]

    if not options:
        raise ValueError(
            "Spell unavailable under verified conditions"
        )

    option = max(
        options,
        key=lambda item: len(item.conditional_rule_ids),
    )

    endurance = calculate_magic_endurance(
        evidence,
        option,
        will_per_attempt=1,
        hypothetical_opportunities=hypothetical_opportunities,
        verify_conditional_rules=bool(
            option.conditional_rule_ids
        ),
    )

    return MagicalEnduranceAssessment(
        profile_id=evidence.profile_id,
        spell_id=spell_id,
        starting_will=endurance.initial_will,
        hypothetical_opportunities=hypothetical_opportunities,
        affordable_attempts=(
            endurance.resource_affordable_attempts
        ),
        modelled_attempts=endurance.modelled_attempts,
        will_spent=endurance.will_consumed,
        remaining_will=endurance.will_remaining,
        probability_per_attempt=(
            endurance.probability_per_attempt
        ),
        expected_successful_casts=(
            endurance.expected_successful_casts
        ),
        applied_rule_ids=option.conditional_rule_ids,
    )
