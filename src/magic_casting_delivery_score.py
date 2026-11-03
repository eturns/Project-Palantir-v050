"""
Project Palantír
DEV-080-F4C: Provisional Magic Casting Delivery.

Author: Edward Turns (Project Lead)

Normalises expected casting output against an
explicit reference opportunity ceiling.

This is a casting-delivery rating, NOT the
complete battlefield Magic capability score.

No production scoring or calibration changes.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class MagicCastingDeliveryScore:
    lower_score: float | None
    upper_score: float | None
    reference_attempts: int
    evidence_status: str
    dashboard_score: None = None
    scenario_score: None = None


def calculate_magic_casting_delivery(
    *,
    expected_successes_lower: float,
    expected_successes_upper: float,
    modelled_attempts: int,
    reference_attempts: int = 12,
) -> MagicCastingDeliveryScore:
    """
    Calculate bounded casting-delivery performance.

    The reference ceiling is an explicit
    provisional benchmark, not an inferred
    universal maximum.

    Refuses unsupported overflow rather than
    silently clipping scores to 1.0.
    """

    if (
        type(reference_attempts) is not int
        or reference_attempts < 1
    ):
        raise ValueError(
            "reference_attempts must be positive"
        )

    if (
        type(modelled_attempts) is not int
        or modelled_attempts < 0
    ):
        raise ValueError(
            "modelled_attempts must be nonnegative"
        )

    for value in (
        expected_successes_lower,
        expected_successes_upper,
    ):
        if (
            type(value) not in (int, float)
            or not isfinite(value)
        ):
            raise ValueError(
                "Expected successes must be finite numbers"
            )

    if not (
        0 <= expected_successes_lower
        <= expected_successes_upper
        <= modelled_attempts
    ):
        raise ValueError(
            "Inconsistent expected casting output"
        )

    if modelled_attempts > reference_attempts:
        return MagicCastingDeliveryScore(
            lower_score=None,
            upper_score=None,
            reference_attempts=reference_attempts,
            evidence_status=(
                "reference_ceiling_exceeded"
            ),
        )

    return MagicCastingDeliveryScore(
        lower_score=(
            expected_successes_lower
            / reference_attempts
        ),
        upper_score=(
            expected_successes_upper
            / reference_attempts
        ),
        reference_attempts=reference_attempts,
        evidence_status=(
            "provisional_casting_delivery_only"
        ),
    )
