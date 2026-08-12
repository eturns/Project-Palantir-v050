"""
Project Palantír
================

File:
    objective_capability_classifier.py

Purpose:
    Classifies normalised optimiser capability scores using Project
    Palantír's shared battlefield rating vocabulary.

Created:
    DEV-054 – Explainable Recommendations
"""

from analysis_constants import (
    AVERAGE,
    EXCEPTIONAL,
    STRONG,
    VERY_WEAK,
    WEAK,
)


VERY_WEAK_MAX = 0.20
WEAK_MAX = 0.40
AVERAGE_MAX = 0.60
STRONG_MAX = 0.80


def classify_objective_capability(
    value: float,
) -> str:
    """
    Classifies a normalised 0–1 optimiser capability score.

    Thresholds are provisional and intended for calibration during
    the REL-0.9 calibration checkpoint.
    """

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            "Objective capability value must be between 0.0 and 1.0."
        )

    if value < VERY_WEAK_MAX:
        return VERY_WEAK

    if value < WEAK_MAX:
        return WEAK

    if value < AVERAGE_MAX:
        return AVERAGE

    if value < STRONG_MAX:
        return STRONG

    return EXCEPTIONAL