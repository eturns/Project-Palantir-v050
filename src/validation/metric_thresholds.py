# =====================================
# Imports
# =====================================

from metric_classifier import (
    classify_metric,
)


# =====================================
# Validation
# =====================================

def validate_metric_thresholds(
    metric_thresholds,
    verbose: bool = False,
) -> None:
    """
    Validate all metric threshold definitions.
    """

    assert metric_thresholds, (
        "Metric thresholds must not be empty."
    )

    for metric_id, threshold in metric_thresholds.items():

        # ------------------------------
        # Metric identity
        # ------------------------------

        assert threshold.metric_id == metric_id, (
            f"Metric threshold ID mismatch "
            f"for '{metric_id}'."
        )

        # ------------------------------
        # Threshold ordering
        # ------------------------------

        assert (
            threshold.very_weak
            < threshold.weak
            < threshold.average
            < threshold.strong
            < threshold.exceptional
        ), (
            f"{metric_id} thresholds are not "
            f"strictly increasing."
        )

        # ------------------------------
        # Boundary behaviour
        # ------------------------------

        assert (
            classify_metric(
                threshold.very_weak,
                threshold,
            )
            == "Very Weak"
        )

        assert (
            classify_metric(
                threshold.weak,
                threshold,
            )
            == "Weak"
        )

        assert (
            classify_metric(
                threshold.average,
                threshold,
            )
            == "Average"
        )

        assert (
            classify_metric(
                threshold.strong,
                threshold,
            )
            == "Strong"
        )

        assert (
            classify_metric(
                threshold.exceptional,
                threshold,
            )
            == "Exceptional"
        )

    print()
    print("========== METRIC THRESHOLDS ==========")
    print(
        f"✓ {len(metric_thresholds)} "
        f"metric thresholds validated"
    )

    if verbose:
        _print_metric_thresholds(
            metric_thresholds,
        )


# =====================================
# Verbose output
# =====================================

def _print_metric_thresholds(
    metric_thresholds,
) -> None:

    print()

    for threshold in metric_thresholds.values():
        print(threshold)