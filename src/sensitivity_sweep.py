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
    results follow the baseline ranking order produced by
    analyse_sensitivity_variant().
    """

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
            )
        )

    return tuple(
        results,
    )