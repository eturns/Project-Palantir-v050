import math

from metric_constants import (
    METRIC_NAMES,
    METRIC_LABELS,
)

from metric_classifier import (
    classify_metric,
)

from metric_queries import (
    get_metric_threshold,
)


# =====================================
# Validation
# =====================================

def validate_metric_interpretation(
    densities,
    metric_thresholds,
    verbose: bool = False,
) -> None:
    """
    Validate the interpretation of every army metric density.
    """

    assert densities is not None, (
        "Army metric densities must be provided."
    )

    assert metric_thresholds, (
        "Metric thresholds must not be empty."
    )

    interpretations = {}

    for metric in METRIC_NAMES:

        # ---------------------------------
        # Density
        # ---------------------------------

        assert hasattr(densities, metric), (
            f"Army metric densities are missing '{metric}'."
        )

        density = getattr(
            densities,
            metric,
        )

        assert isinstance(density, (int, float)), (
            f"Metric density '{metric}' must be numeric."
        )

        assert math.isfinite(density), (
            f"Metric density '{metric}' must be finite."
        )

        assert density >= 0.0, (
            f"Metric density '{metric}' cannot be negative."
        )

        # ---------------------------------
        # Threshold
        # ---------------------------------

        threshold = get_metric_threshold(
            metric,
            metric_thresholds,
        )

        assert threshold is not None, (
            f"No metric threshold found for '{metric}'."
        )

        # ---------------------------------
        # Classification
        # ---------------------------------

        rating = classify_metric(
            density,
            threshold,
        )

        assert isinstance(rating, str), (
            f"Metric rating '{metric}' must be a string."
        )

        assert rating.strip(), (
            f"Metric rating '{metric}' cannot be empty."
        )

        interpretations[metric] = (
            density,
            rating,
        )

    count = len(interpretations)

    label = (
        "metric"
        if count == 1
        else "metrics"
    )

    print()
    print("========== METRIC INTERPRETATION ==========")
    print(
        f"✓ {count} {label} interpreted successfully"
    )

    if verbose:
        _print_metric_interpretation(
            interpretations,
        )


# =====================================
# Verbose output
# =====================================

def _print_metric_interpretation(
    interpretations,
) -> None:

    print()

    for metric in METRIC_NAMES:

        density, rating = interpretations[
            metric
        ]

        print(
            f"{METRIC_LABELS[metric]:14}: "
            f"{density:.2f} ({rating})"
        )