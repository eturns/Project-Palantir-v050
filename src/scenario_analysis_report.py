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
) -> str:
    ranked = rank_scenario_analysis_results(
        results,
    )

    top, bottom = scenario_analysis_extremes(
        ranked,
        count=5,
    )

    return format_scenario_analysis_report(
        top=top,
        bottom=bottom,
    )