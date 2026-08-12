"""
Project Palantír
================

File:
    metric_normalisation.py

Purpose:
    Provides reusable metric normalisation functions for
    optimiser objective scoring.

Created:
    DEV-053 – Objective Functions and Weighting
"""


def normalise_linear(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Normalises a value to the inclusive range 0.0 to 1.0.
    """

    if maximum <= minimum:
        raise ValueError(
            "maximum must be greater than minimum."
        )

    if value <= minimum:
        return 0.0

    if value >= maximum:
        return 1.0

    return (
        value - minimum
    ) / (
        maximum - minimum
    )