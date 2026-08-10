def print_text_analysis_report(
    result: dict,
) -> None:
    """
    Prints a readable Project Palantír army analysis report.
    """

    definition = result[
        "definition"
    ]
    army = result[
        "army"
        ]
    analysis = result[
        "analysis"
    ]

    print("========== IMPORTED ARMY ==========")
    print(f"Name: {definition.name}")
    print(f"Points: {army.total_points()}")
    print(f"Points limit: {definition.points_limit}")
    print()

    validation_errors = analysis[
        "validation_errors"
    ]

    if validation_errors:
        print("Legality issues:")

        for error in validation_errors:
            print(f"- {error}")
    else:
        print("✓ Army is legal.")

    battlefield = analysis[
        "battlefield_assessments"
    ]

    print()
    print("========== ANALYSIS ==========")

    print("Strengths:")

    if battlefield.strengths:
        for assessment in battlefield.strengths:
            metric_name = assessment.metric.replace(
                "_",
                " ",
            ).title()

            print(
                f"✓ {metric_name}: "
                f"{assessment.rating} "
                f"({assessment.value:.2f})"
            )
    else:
        print("None")

    print()
    print("Weaknesses:")

    if battlefield.weaknesses:
        for assessment in battlefield.weaknesses:
            metric_name = assessment.metric.replace(
                "_",
                " ",
            ).title()

            print(
                f"✗ {metric_name}: "
                f"{assessment.rating} "
                f"({assessment.value:.2f})"
            )
    else:
        print("None")