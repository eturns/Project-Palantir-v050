"""
Project Palantír
DEV-080-F3: Turn-Scoped Magic Resource Projection.

Author: Edward Turns (Project Lead)

Projects hypothetical Will expenditure across turns.

Temporary Will:
- Is granted separately each turn.
- Is spent before permanent Will.
- Expires if unused.
- Never transfers between turns.

Diagnostic only. Does not modify actual resource
ledgers, scenarios or calibrated scores.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MagicTurnResource:
    turn: int
    requested_attempts: int
    funded_attempts: int
    temporary_will_spent: int
    permanent_will_spent: int
    permanent_will_remaining: int


@dataclass(frozen=True)
class MagicResourceProjection:
    modelled_attempts: int
    funded_attempts: int
    temporary_will_spent: int
    permanent_will_spent: int
    permanent_will_remaining: int
    turns: tuple[MagicTurnResource, ...]
    evidence_status: str = (
        "conditional_turn_scoped_resource_projection"
    )
    dashboard_score: None = None
    scenario_score: None = None


def project_magic_resources(
    *,
    starting_permanent_will: int,
    temporary_will_per_turn: int,
    attempts_by_turn: tuple[int, ...],
) -> MagicResourceProjection:
    """
    Project one-Will casting attempts.

    The caller supplies a legal hypothetical
    attempt schedule and an evidence-backed
    temporary Will grant.

    Other Will expenditure is not modelled.
    """

    for name, value in (
        ("starting_permanent_will",
         starting_permanent_will),
        ("temporary_will_per_turn",
         temporary_will_per_turn),
    ):
        if type(value) is not int:
            raise TypeError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} must be nonnegative")

    if not isinstance(attempts_by_turn, tuple):
        raise TypeError("attempts_by_turn must be a tuple")

    for attempts in attempts_by_turn:
        if type(attempts) is not int:
            raise TypeError("Attempt counts must be integers")
        if attempts < 0:
            raise ValueError(
                "Attempt counts must be nonnegative"
            )

    remaining = starting_permanent_will
    turn_results = []

    for turn_number, requested in enumerate(
        attempts_by_turn, start=1
    ):
        # The temporary grant is fresh each turn.
        # Unused temporary Will never carries forward.
        temporary_spent = min(
            requested,
            temporary_will_per_turn,
        )

        permanent_spent = min(
            requested - temporary_spent,
            remaining,
        )

        funded = temporary_spent + permanent_spent
        remaining -= permanent_spent

        turn_results.append(
            MagicTurnResource(
                turn=turn_number,
                requested_attempts=requested,
                funded_attempts=funded,
                temporary_will_spent=temporary_spent,
                permanent_will_spent=permanent_spent,
                permanent_will_remaining=remaining,
            )
        )

    return MagicResourceProjection(
        modelled_attempts=sum(attempts_by_turn),
        funded_attempts=sum(
            turn.funded_attempts
            for turn in turn_results
        ),
        temporary_will_spent=sum(
            turn.temporary_will_spent
            for turn in turn_results
        ),
        permanent_will_spent=sum(
            turn.permanent_will_spent
            for turn in turn_results
        ),
        permanent_will_remaining=remaining,
        turns=tuple(turn_results),
    )