from scenario_analysis_result import ScenarioAnalysisResult
from scenario_catalogue import get_official_scenarios
from scenario_fit import calculate_scenario_definition_fit
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)
from scenario_demand_analysis import ScenarioDemandAnalysis
from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
)
from scenario_preservation_profile import (
    select_fog_of_war_preservation_profile,
)
from scenario_demand import StrategicDemand

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
    *,
    scenario_capability_overrides=None,
) -> tuple[ScenarioAnalysisResult, ...]:
    capabilities = capability_profile.to_mapping()

    if scenario_capability_overrides is None:
        scenario_capability_overrides = {}

    results = []

    for scenario in get_official_scenarios():
        scenario_capabilities = dict(capabilities)

        scenario_capabilities.update(
            scenario_capability_overrides.get(
                scenario.id,
                {},
            )
        )

        results.append(
            ScenarioAnalysisResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                pool=scenario.pool,
                score=calculate_scenario_definition_fit(
                    scenario=scenario,
                    capabilities=scenario_capabilities,
                ).score,
                demands=tuple(
                    ScenarioDemandAnalysis(
                        dimension=demand.dimension,
                        capability=scenario_capabilities[
                            demand.dimension
                        ],
                        intensity=demand.intensity,
                    )
                    for demand in scenario.strategic_demands
                ),
            )
        )

    return tuple(results)

def build_scenario_analysis_results_from_candidate(
    *,
    candidate,
    army_list=None,
    key_profile=None,
    leader_profile=None,
    preservation_profile=None,
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
        preservation_profile=preservation_profile,
        combat_benchmark=combat_benchmark,
        benchmark_presence=benchmark_presence,
        benchmark_manoeuvrability=benchmark_manoeuvrability,
        benchmark_combat_capability=benchmark_combat_capability,
        benchmark_fate=benchmark_fate,
        resurrection_config=resurrection_config,
    )
)
    scenario_capability_overrides = {}

    if (
        leader_profile is not None
        and combat_benchmark is not None
        and benchmark_fate is not None
    ):
        fog_profile = (
            select_fog_of_war_preservation_profile(
                army=candidate.army,
                leader_profile=leader_profile,
                combat_benchmark=combat_benchmark,
                benchmark_fate=benchmark_fate,
            )
        )

        if fog_profile is not None:
            fog_preservation = (
                calculate_key_model_preservation_from_profile(
                    profile=fog_profile,
                    benchmark=combat_benchmark,
                    benchmark_fate=benchmark_fate,
                    army=candidate.army,
                    army_list=army_list,
                )
            )

            scenario_capability_overrides[
                "FOG_OF_WAR"
            ] = {
                StrategicDemand.KEY_MODEL_PRESERVATION:
                    fog_preservation.value,
            }

    return build_scenario_analysis_results_from_profile(
        capability_profile,
        scenario_capability_overrides=(
            scenario_capability_overrides
        ),
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