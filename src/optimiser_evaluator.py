"""
Project Palantír
================

File:
    optimiser_evaluator.py

Purpose:
    Evaluates optimiser candidates against an objective
    and supplied constraints.

Created:
    DEV-051 – Optimiser Foundation
"""

from optimiser_candidate import OptimiserCandidate
from optimiser_constraint import OptimiserConstraint
from optimiser_evaluation import OptimiserEvaluation
from optimiser_objective import OptimiserObjective


def evaluate_candidate(
    candidate: OptimiserCandidate,
    objective: OptimiserObjective,
    constraints: tuple[OptimiserConstraint, ...] = (),
) -> OptimiserEvaluation:
    """
    Evaluates one optimiser candidate.

    Returns the objective score together with any
    constraint validation errors.
    """

    errors = []

    for constraint in constraints:
        errors.extend(
            constraint.validate(candidate)
        )

    score = objective.evaluate(candidate)

    return OptimiserEvaluation(
        candidate=candidate,
        score=score,
        errors=tuple(errors),
    )