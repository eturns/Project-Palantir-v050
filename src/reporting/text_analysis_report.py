from scenario_analysis_report import (
    build_scenario_analysis_report,
)


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

    evidence_records = result.get(
        "evidence_records",
        (),
    )
    scenario_analysis_results = result.get(
            "scenario_analysis_results",
        )
    
    if evidence_records and scenario_analysis_results is None:
        print()
        print("========== EVIDENCE & LIMITATIONS ==========")

        for evidence in evidence_records:
            mechanic_name = evidence.mechanic.replace(
                "_",
                " ",
            ).title()

            print(
                f"{mechanic_name}: "
                f"{evidence.status.value.upper()}"
            )

            print(f"  Reason: {evidence.reason}")
            print(f"  Source: {evidence.provenance}")

    if scenario_analysis_results is not None:
        print()
        print("========== SCENARIO ANALYSIS ==========")
        print(
            build_scenario_analysis_report(
                scenario_analysis_results,
                evidence_records=evidence_records,
            )
        )