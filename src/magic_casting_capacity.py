
"""
Project Palantír
DEV-080-D1: Casting Capacity.

Author: Edward Turns (Project Lead)

Diagnostic-only calculation of casting attempt ceilings.

No invented battlefield targets, successful casts,
or actual casting opportunities.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MagicCastingCapacity:
    starting_will: int
    hypothetical_activations: int
    distinct_spell_count: int
    permitted_attempts_per_activation: int
    spell_distinct_attempt_ceiling: int
    opportunity_attempt_ceiling: int
    resource_attempt_ceiling: int
    modelled_attempt_ceiling: int
    remaining_will_at_ceiling: int

    evidence_status: str = "conditional_capacity_ceiling"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_casting_capacity(
    *,
    starting_will: int,
    hypothetical_activations: int = 6,
    distinct_spell_count: int,
    permitted_attempts_per_activation: int = 1,
) -> MagicCastingCapacity:
    """
    Calculate the maximum number of hypothetical
    one-Will casting attempts.

    Each attempted cast consumes one Will.

    Additional attempts in the same activation
    must use distinct spells. The calculation
    cannot establish that separate legal targets
    or suitable opportunities exist.
    """

    inputs = (
        ("starting_will", starting_will, 0),
        ("hypothetical_activations", hypothetical_activations, 0),
        ("distinct_spell_count", distinct_spell_count, 0),
        (
            "permitted_attempts_per_activation",
            permitted_attempts_per_activation,
            1,
        ),
    )

    for name, value, minimum in inputs:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")

        if value < minimum:
            raise ValueError(
                f"{name} must be at least {minimum}"
            )

    distinct_ceiling = min(
        permitted_attempts_per_activation,
        distinct_spell_count,
    )

    opportunity_ceiling = (
        hypothetical_activations * distinct_ceiling
    )

    resource_ceiling = starting_will

    modelled_ceiling = min(
        opportunity_ceiling,
        resource_ceiling,
    )

    return MagicCastingCapacity(
        starting_will=starting_will,
        hypothetical_activations=hypothetical_activations,
        distinct_spell_count=distinct_spell_count,
        permitted_attempts_per_activation=(
            permitted_attempts_per_activation
        ),
        spell_distinct_attempt_ceiling=distinct_ceiling,
        opportunity_attempt_ceiling=opportunity_ceiling,
        resource_attempt_ceiling=resource_ceiling,
        modelled_attempt_ceiling=modelled_ceiling,
        remaining_will_at_ceiling=(
            starting_will - modelled_ceiling
        ),
    )
