"""
Compatibility layer for objective normalisation.

Canonical implementations now live in:
    objective_normalisation.py

This module remains temporarily to preserve existing imports
while DEV-053 migrates callers to the new objective-level
normalisation architecture.
"""

from objective_normalisation import (
    CONTROL_DENSITY_MAX,
    MAGIC_DENSITY_MAX,
    MANOEUVRABILITY_MAX,
    MODEL_PRESENCE_MAX_PER_100_POINTS,
    normalise_control,
    normalise_magic,
    normalise_manoeuvrability,
    normalise_model_presence,
)

__all__ = [
    "CONTROL_DENSITY_MAX",
    "MAGIC_DENSITY_MAX",
    "MANOEUVRABILITY_MAX",
    "MODEL_PRESENCE_MAX_PER_100_POINTS",
    "normalise_control",
    "normalise_magic",
    "normalise_manoeuvrability",
    "normalise_model_presence",
]