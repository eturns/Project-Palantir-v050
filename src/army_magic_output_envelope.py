"""
Project Palantír
DEV-080-F2: Army Casting Output Envelope.

Author: Edward Turns (Project Lead)

Combines separate caster output envelopes.

Diagnostic only. No transfers of Will between
casters and no invented battlefield opportunities.
"""

from dataclasses import dataclass
from math import fsum

from magic_casting_output_envelope import (
    calculate_casting_output_envelope,
)


@dataclass(frozen=True)
class ArmyMagicOutputEnvelope:
    caster_count: int
    modelled_attempts: int
    minimum_expected_successes: float
    maximum_expected_successes: float
    caster_results: tuple
    evidence_status: str = (
        "conditional_army_casting_output"
    )
    dashboard_score: None = None
    scenario_score: None = None


def assess_army_magic_output(
    army_magic_assessment,
) -> ArmyMagicOutputEnvelope:
    """
    Combine caster output under a common
    six-activation reference window.

    Spell selections remain conditional.
    """
    effectiveness = dict(
        army_magic_assessment.caster_effectiveness
    )
    capacities = dict(
        army_magic_assessment.caster_capacity
    )

    if set(effectiveness) != set(capacities):
        raise ValueError(
            "Caster effectiveness and capacity IDs differ"
        )

    results = []

    for model_id in sorted(effectiveness):
        casting = effectiveness[model_id]
        capacity = capacities[model_id]

        probabilities = tuple(
            (spell_id, enhanced)
            for spell_id, baseline, enhanced
            in casting.spell_results
        )

        envelope = calculate_casting_output_envelope(
            spell_probabilities=probabilities,
            starting_will=capacity.starting_will,
            hypothetical_activations=(
                capacity.hypothetical_activations
            ),
            permitted_attempts_per_activation=(
                capacity.permitted_attempts_per_activation
            ),
        )

        if (
            envelope.modelled_attempts
            != capacity.modelled_attempt_ceiling
        ):
            raise ValueError(
                "Casting output and capacity disagree"
            )

        results.append((model_id, envelope))

    return ArmyMagicOutputEnvelope(
        caster_count=len(results),
        modelled_attempts=sum(
            item.modelled_attempts
            for _, item in results
        ),
        minimum_expected_successes=fsum(
            item.minimum_expected_successes
            for _, item in results
        ),
        maximum_expected_successes=fsum(
            item.maximum_expected_successes
            for _, item in results
        ),
        caster_results=tuple(results),
    )