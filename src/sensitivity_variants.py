"""
Project Palantír
================

File:
    sensitivity_variants.py

Purpose:
    Builds controlled objective-weight variants for optimiser
    sensitivity analysis.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass

from objective_preset import ObjectivePreset
from objective_weight_variation import (
    vary_objective_weight,
)


@dataclass(frozen=True)
class SensitivityVariant:
    """
    Represents one controlled variation of an objective preset.
    """

    varied_capability: str
    baseline_weight: float
    variant_weight: float
    preset: ObjectivePreset


def build_sensitivity_variants(
    *,
    preset: ObjectivePreset,
    delta: float,
) -> tuple[SensitivityVariant, ...]:
    """
    Builds lower and upper weight variants for every capability.

    Variant order follows the baseline preset order, with the lower
    weight variant appearing before the upper weight variant.

    Raises:
        ValueError:
            If delta is not positive.
    """

    if delta <= 0.0:
        raise ValueError(
            "Sensitivity delta must be greater than zero."
        )

    variants = []

    for weight in preset.weights:
        lower_weight = (
            weight.weight
            - delta
        )

        upper_weight = (
            weight.weight
            + delta
        )

        if lower_weight >= 0.0:
            variants.append(
                SensitivityVariant(
                    varied_capability=weight.name,
                    baseline_weight=weight.weight,
                    variant_weight=lower_weight,
                    preset=vary_objective_weight(
                        preset=preset,
                        capability=weight.name,
                        variant_weight=lower_weight,
                    ),
                )
            )

        if upper_weight <= 1.0:
            variants.append(
                SensitivityVariant(
                    varied_capability=weight.name,
                    baseline_weight=weight.weight,
                    variant_weight=upper_weight,
                    preset=vary_objective_weight(
                        preset=preset,
                        capability=weight.name,
                        variant_weight=upper_weight,
                    ),
                )
            )

    return tuple(
        variants,
    )