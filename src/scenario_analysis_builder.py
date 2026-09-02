from scenario_analysis_result import ScenarioAnalysisResult
from scenario_catalogue import get_official_scenarios
from scenario_fit import calculate_scenario_definition_fit
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)
from scenario_demand_analysis import ScenarioDemandAnalysis

def build_scenario_analysis_results(
    *,
    scenario_scores,
) -> tuple[ScenarioAnalysisResult, ...]:
    return tuple(
        ScenarioAnalysisResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            pool=pool,
            score=score,
        )
        for (
            scenario_id,
            scenario_name,
            pool,
            score,
        ) in scenario_scores
    )


def build_scenario_analysis_results_from_profile(
    capability_profile,
) -> tuple[ScenarioAnalysisResult, ...]:
    capabilities = capability_profile.to_mapping()

    return tuple(
        ScenarioAnalysisResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            pool=scenario.pool,
            score=calculate_scenario_definition_fit(
                scenario=scenario,
                capabilities=capabilities,
            ).score,
            demands=tuple(
                ScenarioDemandAnalysis(
                    dimension=demand.dimension,
                    capability=capabilities[
                        demand.dimension
                    ],
                    intensity=demand.intensity,
                )
                for demand in scenario.strategic_demands
            ),
        )
        for scenario in get_official_scenarios()
    )

def build_scenario_analysis_results_from_candidate(
    *,
    candidate,
    army_list=None,
    key_profile=None,
    combat_benchmark=None,
    benchmark_presence=None,
    benchmark_manoeuvrability=None,
    benchmark_combat_capability=None,
    benchmark_fate=None,
    resurrection_config=None,
) -> tuple[ScenarioAnalysisResult, ...]:
    capability_profile = (
        build_scenario_capability_profile_from_candidate(
            candidate,
            army_list=army_list,
            key_profile=key_profile,
            combat_benchmark=combat_benchmark,
            benchmark_presence=benchmark_presence,
            benchmark_manoeuvrability=benchmark_manoeuvrability,
            benchmark_combat_capability=benchmark_combat_capability,
            benchmark_fate=benchmark_fate,
            resurrection_config=resurrection_config,
        )
    )

    return build_scenario_analysis_results_from_profile(
        capability_profile,
    )

def rank_scenario_analysis_results(
    results: tuple[ScenarioAnalysisResult, ...],
) -> tuple[ScenarioAnalysisResult, ...]:
    return tuple(
        sorted(
            results,
            key=lambda result: result.score,
            reverse=True,
        )
    )

def scenario_analysis_extremes(
    ranked_results: tuple[ScenarioAnalysisResult, ...],
    *,
    count: int,
) -> tuple[
    tuple[ScenarioAnalysisResult, ...],
    tuple[ScenarioAnalysisResult, ...],
]:
    top = ranked_results[:count]

    bottom = ranked_results[
        len(ranked_results) - count:
    ]

    return top, bottom