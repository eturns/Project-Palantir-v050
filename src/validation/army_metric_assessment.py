import math

from army_metric_assessment import (
    assess_army_metrics,
)

from metric_constants import (
    METRIC_LABELS,
    METRIC_NAMES,
)


# =====================================
# Validation
# =====================================

def validate_army_metric_assessments(
    assessments,
    verbose: bool = False,
) -> None:
    """
    Validate army metric assessments.
    """
  
    assert assessments is not None, (
        "Army metric assessments were not calculated."
    )

    assert isinstance(assessments, list), (
        "Army metric assessments must be returned as a list."
    )

    assert len(assessments) == len(METRIC_NAMES), (
        "An assessment must exist for every metric."
    )

    assessed_metrics = set()

    for assessment in assessments:

        assert hasattr(assessment, "metric"), (
            "Army metric assessment is missing 'metric'."
        )

        assert assessment.metric in METRIC_NAMES, (
            f"Unknown assessment metric: "
            f"'{assessment.metric}'."
        )

        assert assessment.metric not in assessed_metrics, (
            f"Duplicate assessment for "
            f"'{assessment.metric}'."
        )

        assessed_metrics.add(
            assessment.metric,
        )

        assert hasattr(assessment, "value"), (
            f"Assessment '{assessment.metric}' "
            "is missing 'value'."
        )

        assert isinstance(
            assessment.value,
            (int, float),
        ), (
            f"Assessment value '{assessment.metric}' "
            "must be numeric."
        )

        assert math.isfinite(
            assessment.value,
        ), (
            f"Assessment value '{assessment.metric}' "
            "must be finite."
        )

        assert assessment.value >= 0.0, (
            f"Assessment value '{assessment.metric}' "
            "cannot be negative."
        )

        assert hasattr(assessment, "rating"), (
            f"Assessment '{assessment.metric}' "
            "is missing 'rating'."
        )

        assert isinstance(
            assessment.rating,
            str,
        ), (
            f"Assessment rating '{assessment.metric}' "
            "must be a string."
        )

        assert assessment.rating.strip(), (
            f"Assessment rating '{assessment.metric}' "
            "cannot be empty."
        )

    count = len(assessments)

    label = (
        "assessment"
        if count == 1
        else "assessments"
    )

    print()
    print(
        "========== ARMY METRIC ASSESSMENTS =========="
    )
    print(
        f"✓ {count} metric {label} validated"
    )

    if verbose:
        _print_army_metric_assessments(
            assessments,
        )


# =====================================
# Verbose output
# =====================================

def _print_army_metric_assessments(
    assessments,
) -> None:

    print()

    for assessment in assessments:

        print(
            f"{METRIC_LABELS[assessment.metric]:14}: "
            f"{assessment.value:.2f} "
            f"({assessment.rating})"
        )