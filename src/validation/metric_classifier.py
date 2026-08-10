# =====================================
# Imports
# =====================================

from metric_classifier import (
    classify_metric,
)


# =====================================
# Constants
# =====================================

EXPECTED_RATINGS = (
    "Very Weak",
    "Weak",
    "Average",
    "Strong",
    "Exceptional",
)


# =====================================
# Validation
# =====================================

def validate_metric_classifier(
    metric_thresholds,
    verbose: bool = False,
) -> None:
    """
    Validate that metric values are classified correctly
    against every loaded metric threshold.
    """

    assert metric_thresholds, (
        "Metric thresholds must not be empty."
    )

    for metric_id, threshold in metric_thresholds.items():

        test_cases = (
            (
                0.0,
                "Very Weak",
            ),
            (
                threshold.weak,
                "Weak",
            ),
            (
                threshold.average,
                "Average",
            ),
            (
                threshold.strong,
                "Strong",
            ),
            (
                threshold.exceptional,
                "Exceptional",
            ),
            (
                threshold.exceptional + 1.0,
                "Exceptional",
            ),
        )

        for value, expected_rating in test_cases:

            actual_rating = classify_metric(
                value,
                threshold,
            )

            assert actual_rating in EXPECTED_RATINGS, (
                f"{metric_id} returned unknown rating "
                f"'{actual_rating}'."
            )

            assert actual_rating == expected_rating, (
                f"{metric_id} value {value:.2f} returned "
                f"'{actual_rating}'; expected "
                f"'{expected_rating}'."
            )

    print()
    print("========== METRIC CLASSIFIER ==========")
    print(
        f"✓ Metric classification validated "
        f"for {len(metric_thresholds)} metrics"
    )

    if verbose:
        _print_metric_classifier(
            metric_thresholds,
        )


# =====================================
# Verbose output
# =====================================

def _print_metric_classifier(
    metric_thresholds,
) -> None:

    print()

    for metric_id, threshold in metric_thresholds.items():

        print(metric_id)
        print(
            f"  0.00 -> "
            f"{classify_metric(0.0, threshold)}"
        )
        print(
            f"  {threshold.weak:.2f} -> "
            f"{classify_metric(threshold.weak, threshold)}"
        )
        print(
            f"  {threshold.average:.2f} -> "
            f"{classify_metric(threshold.average, threshold)}"
        )
        print(
            f"  {threshold.strong:.2f} -> "
            f"{classify_metric(threshold.strong, threshold)}"
        )
        print(
            f"  {threshold.exceptional:.2f} -> "
            f"{classify_metric(threshold.exceptional, threshold)}"
        )
        print()