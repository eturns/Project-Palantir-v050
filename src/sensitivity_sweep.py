"""
Project Palantír
================

File:
    sensitivity_sweep.py

Purpose:
    Runs sensitivity analysis across multiple controlled
    objective-weight variants.

Created:
    DEV-054 – Explainable Recommendations
"""

from sensitivity_analysis import (
    _rank_candidates,
    analyse_sensitivity_variant,
)


def analyse_sensitivity_sweep(
    *,
    candidates,
    baseline_objective,
    variants,
    objective_factory,
):
    """
    Runs sensitivity analysis for every supplied variant.

    Results are returned in variant order. Within each variant,
    results follow the shared baseline ranking order.

    The baseline ranking is calculated once and reused across all
    sensitivity variants.
    """

    if not variants:
        return ()

    baseline_ranking = _rank_candidates(
        candidates=candidates,
        objective=baseline_objective,
    )

    results = []

    for variant in variants:
        variant_objective = objective_factory(
            variant.preset,
        )

        results.extend(
            analyse_sensitivity_variant(
                candidates=candidates,
                baseline_objective=baseline_objective,
                variant_objective=variant_objective,
                variant=variant,
                baseline_ranking=baseline_ranking,
            )
        )

    return tuple(
        results,
    )