"""
Project Palantír
================

File:
    objective_weight_variation.py

Purpose:
    Creates controlled objective-weight variants for optimiser
    sensitivity analysis.

Created:
    DEV-054 – Explainable Recommendations
"""

from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight


def vary_objective_weight(
    *,
    preset: ObjectivePreset,
    capability: str,
    variant_weight: float,
) -> ObjectivePreset:
    """
    Returns a new preset with one capability assigned the requested
    weight while all remaining weights are rescaled proportionally.

    The original preset is not modified.
    """

    if not 0.0 <= variant_weight <= 1.0:
        raise ValueError(
            "Variant weight must be between 0.0 and 1.0."
        )

    weights_by_name = {
        weight.name: weight
        for weight in preset.weights
    }

    if capability not in weights_by_name:
        raise ValueError(
            f"Unknown objective capability: {capability}"
        )

    baseline_target_weight = weights_by_name[
        capability
    ].weight

    baseline_other_total = (
        1.0
        - baseline_target_weight
    )

    variant_other_total = (
        1.0
        - variant_weight
    )

    variant_weights = []

    for weight in preset.weights:
        if weight.name == capability:
            new_weight = variant_weight

        else:
            if baseline_other_total == 0.0:
                raise ValueError(
                    "Cannot rescale other objective weights when "
                    "the selected capability already has all weight."
                )

            new_weight = (
                weight.weight
                / baseline_other_total
                * variant_other_total
            )

        variant_weights.append(
            ObjectiveWeight(
                name=weight.name,
                weight=new_weight,
            )
        )

    return ObjectivePreset(
        name=preset.name,
        weights=tuple(
            variant_weights,
        ),
    )