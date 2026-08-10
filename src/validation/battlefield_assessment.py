from battlefield_assessment import (
    assess_battlefield,
)

from metric_description_queries import (
    get_metric_description,
)


# =====================================
# Validation
# =====================================

def validate_battlefield_assessment(
    assessments,
    metric_descriptions,
    verbose: bool = False,
) -> None:
    """
    Validate the battlefield strengths and weaknesses
    produced from army metric assessments.
    """

    assert assessments is not None, (
        "Army metric assessments must be provided."
    )

    assert isinstance(assessments, list), (
        "Army metric assessments must be a list."
    )

    assert metric_descriptions, (
        "Metric descriptions must not be empty."
    )

    battlefield = assess_battlefield(
        assessments,
    )

    assert battlefield is not None, (
        "Battlefield assessment was not produced."
    )

    assert hasattr(battlefield, "strengths"), (
        "Battlefield assessment is missing 'strengths'."
    )

    assert isinstance(battlefield.strengths, list), (
        "Battlefield strengths must be a list."
    )

    assert hasattr(battlefield, "weaknesses"), (
        "Battlefield assessment is missing 'weaknesses'."
    )

    assert isinstance(battlefield.weaknesses, list), (
        "Battlefield weaknesses must be a list."
    )

    for assessment in (
        battlefield.strengths
        + battlefield.weaknesses
    ):

        assert hasattr(assessment, "metric"), (
            "Battlefield assessment entry is missing 'metric'."
        )

        description = get_metric_description(
            assessment.metric,
            metric_descriptions,
        )

        assert description is not None, (
            f"No metric description found for "
            f"'{assessment.metric}'."
        )

    print()
    print(
        "========== BATTLEFIELD ASSESSMENT =========="
    )
    print("✓ Battlefield assessment validated")

    if verbose:
        _print_battlefield_assessment(
            battlefield,
            metric_descriptions,
        )


# =====================================
# Verbose output
# =====================================

def _print_battlefield_assessment(
    battlefield,
    metric_descriptions,
) -> None:

    print()
    print("Strengths")
    print("---------")

    if battlefield.strengths:

        for assessment in battlefield.strengths:

            description = get_metric_description(
                assessment.metric,
                metric_descriptions,
            )

            print(
                f"✓ "
                f"{description.strength_description}"
            )

    else:
        print("None")

    print()
    print("Weaknesses")
    print("----------")

    if battlefield.weaknesses:

        for assessment in battlefield.weaknesses:

            description = get_metric_description(
                assessment.metric,
                metric_descriptions,
            )

            print(
                f"✗ "
                f"{description.weakness_description}"
            )

    else:
        print("None")