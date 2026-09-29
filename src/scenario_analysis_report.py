from scenario_analysis_result import ScenarioAnalysisResult
from scenario_analysis_builder import (
    rank_scenario_analysis_results,
    scenario_analysis_extremes,
)

def _format_scenario_result(
    result: ScenarioAnalysisResult,
) -> str:
    lines = [
        (
            f"{result.scenario_name} "
            f"({result.pool.value}) "
            f"- {result.score:.3f}"
        ),
    ]

    for demand in result.demands:
        lines.append(
            (
                f"  {demand.dimension.value}: "
                f"{demand.capability:.3f}"
            )
        )

    return "\n".join(
        lines
    )


def format_scenario_analysis_report(
    *,
    top: tuple[ScenarioAnalysisResult, ...],
    bottom: tuple[ScenarioAnalysisResult, ...],
) -> str:
    sections = [
        "Top Scenarios",
        *(
            _format_scenario_result(
                result,
            )
            for result in top
        ),
        "",
        "Bottom Scenarios",
        *(
            _format_scenario_result(
                result,
            )
            for result in bottom
        ),
    ]

    return "\n".join(
        sections
    )

def build_scenario_analysis_report(
    results: tuple[ScenarioAnalysisResult, ...],
    *,
    evidence_records=(),
) -> str:
    ranked = rank_scenario_analysis_results(
        results,
    )

    top, bottom = scenario_analysis_extremes(
        ranked,
        count=5,
    )

    report = format_scenario_analysis_report(
        top=top,
        bottom=bottom,
    )

    if not evidence_records:
        return report

    evidence_lines = [
        "",
        "========== EVIDENCE & LIMITATIONS ==========",
    ]

    for evidence in evidence_records:
        mechanic_name = evidence.mechanic.replace(
            "_",
            " ",
        ).title()

        evidence_lines.extend(
            [
                (
                    f"{mechanic_name}: "
                    f"{evidence.status.value.upper()}"
                ),
                f"  Reason: {evidence.reason}",
                f"  Source: {evidence.provenance}",
            ]
        )

    return report + "\n" + "\n".join(evidence_lines)