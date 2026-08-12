"""
Project Palantír
================

File:
    explainable_recommendation_service.py

Purpose:
    Builds ranked explainable optimiser recommendations from a
    candidate pool.

Created:
    DEV-054 – Explainable Recommendations
"""

from marginal_swap_lookup import (
    build_marginal_swap_lookup,
)
from optimiser_evaluation import OptimiserEvaluation
from recommendation_builder import (
    build_recommendations,
)
from optimiser_candidate_key import (
    build_candidate_key,
)
from sensitivity_stability import (
    summarise_candidate_stability,
)
from sensitivity_sweep import (
    analyse_sensitivity_sweep,
)
from sensitivity_variants import (
    build_sensitivity_variants,
)

def build_explainable_recommendations(
    *,
    candidates,
    objective,
    constraints=(),
    sensitivity_preset=None,
    sensitivity_objective_factory=None,
    sensitivity_delta=0.05,
):
    """
    Evaluates candidates and returns ranked explainable recommendations.

    Current integration includes:
        - objective evaluation
        - transparent objective scores
        - constraint errors
        - ranked marginal swap analysis

    Sensitivity integration is added in the next increment.
    """

    if not candidates:
        return ()

    evaluations = []

    for candidate in candidates:
        constraint_errors = []

        for constraint in constraints:
            constraint_errors.extend(
                constraint.validate(
                    candidate,
                )
            )

        evaluations.append(
            OptimiserEvaluation(
                candidate=candidate,
                score=objective.evaluate(
                    candidate,
                ),
                errors=tuple(
                    constraint_errors,
                ),
            )
        )

    marginal_swaps_by_candidate = (
        build_marginal_swap_lookup(
            candidates=candidates,
            objective=objective,
            constraints=constraints,
        )
    )
    sensitivity_stability_by_candidate = None

    if (
        sensitivity_preset is not None
        and sensitivity_objective_factory is not None
    ):
        variants = build_sensitivity_variants(
            preset=sensitivity_preset,
            delta=sensitivity_delta,
        )

        sensitivity_results = analyse_sensitivity_sweep(
            candidates=candidates,
            baseline_objective=objective,
            variants=variants,
            objective_factory=sensitivity_objective_factory,
        )

        sensitivity_stability_by_candidate = {
            id(candidate): summarise_candidate_stability(
                candidate_key=build_candidate_key(
                    candidate,
                ),
                results=sensitivity_results,
            )
            for candidate in candidates
        }
        
    return build_recommendations(
        tuple(
            evaluations,
        ),
        objective=objective,
        marginal_swaps_by_candidate=(
            marginal_swaps_by_candidate
        ),
        sensitivity_stability_by_candidate=(
            sensitivity_stability_by_candidate
        ),
    )