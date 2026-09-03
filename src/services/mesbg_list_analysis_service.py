from optimiser_candidate import OptimiserCandidate
from scenario_analysis_builder import (
    build_scenario_analysis_results_from_candidate,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from services.army_analysis_service import (
    analyse_imported_army,
)
from scenario_analysis_context import (
    build_default_scenario_analysis_context,
)

def analyse_mesbg_list_builder_file(
    file_path: str,
    profiles_by_id: dict,
    army_lists_by_id: dict,
    metric_thresholds,
    *,
    key_profile=None,
    combat_benchmark=None,
    benchmark_presence=None,
    benchmark_manoeuvrability=None,
    benchmark_combat_capability=None,
    benchmark_fate=None,
    resurrection_config=None,
) -> dict:
    """
    Imports an MESBG List Builder file and runs the complete
    Project Palantír analysis pipeline.
    """

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            file_path,
            profiles_by_id,
            army_lists_by_id,
        )
    )

    leader_profile = None

    leader_profile_id = getattr(
        definition,
        "leader_profile_id",
        None,
    )

    if leader_profile_id is not None:
        leader_profile = profiles_by_id[
            leader_profile_id
        ]

    if key_profile is None:
            key_profile = leader_profile

    default_scenario_context = (
        build_default_scenario_analysis_context(
            points_limit=definition.points_limit,
        )
    )

    if combat_benchmark is None:
        combat_benchmark = (
            default_scenario_context.combat_benchmark
        )

    if benchmark_presence is None:
        benchmark_presence = (
            default_scenario_context.benchmark_presence
        )

    if benchmark_manoeuvrability is None:
        benchmark_manoeuvrability = (
            default_scenario_context.benchmark_manoeuvrability
        )

    if benchmark_combat_capability is None:
        benchmark_combat_capability = (
            default_scenario_context.benchmark_combat_capability
        )

    if benchmark_fate is None:
        benchmark_fate = (
            default_scenario_context.benchmark_fate
        )

    analysis_result = analyse_imported_army(
        army,
        army_list,
        definition.points_limit,
        metric_thresholds,
    )

    scenario_analysis_results = None

    if all(
        value is not None
        for value in (
            key_profile,
            combat_benchmark,
            benchmark_presence,
            benchmark_manoeuvrability,
            benchmark_combat_capability,
            benchmark_fate,
        )
    ):
        candidate = OptimiserCandidate(
            army=army,
        )

        scenario_analysis_results = (
            build_scenario_analysis_results_from_candidate(
                candidate=candidate,
                army_list=army_list,
                key_profile=key_profile,
                leader_profile=leader_profile,
                preservation_profile=leader_profile,
                combat_benchmark=combat_benchmark,
                benchmark_presence=benchmark_presence,
                benchmark_manoeuvrability=(
                    benchmark_manoeuvrability
                ),
                benchmark_combat_capability=(
                    benchmark_combat_capability
                ),
                benchmark_fate=benchmark_fate,
                resurrection_config=resurrection_config,
            )
        )

    return {
        "definition": definition,
        "army": army,
        "army_list": army_list,
        "analysis": analysis_result,
        "scenario_analysis_results": (
            scenario_analysis_results
        ),
    }