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
from resurrection_config import ResurrectionConfig
from fielded_model_structure_builder import (
    build_fielded_model_structures,
)
from importers.mesbg_list_builder_fielded_structure_map import (
    FIELDED_MODEL_STRUCTURE_DEFINITIONS,
)
from fielded_model_form_state_initialization import (
    get_initial_fielded_model_form_states,
)
from importers.mesbg_list_builder_alternate_form_map import (
    ALLOWED_ALTERNATE_FORMS_BY_PROFILE_ID,
)

def analyse_mesbg_list_builder_file(
    file_path: str,
    profiles_by_id: dict,
    army_lists_by_id: dict,
    metric_thresholds,
    *,
    profile_options_by_external_id: dict | None = None,
    siege_engine_profiles_by_id: dict | None = None,
    key_profile=None,
    combat_benchmark=None,
    benchmark_presence=None,
    benchmark_manoeuvrability=None,
    benchmark_combat_capability=None,
    benchmark_fate=None,
    resurrection_config: ResurrectionConfig | None = None,
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
            profile_options_by_external_id=
                profile_options_by_external_id,
            siege_engine_profiles_by_id=
                siege_engine_profiles_by_id,
        )
    )

    fielded_models = army.fielded_models()

    fielded_model_structures = (
        build_fielded_model_structures(
            fielded_models=fielded_models,
            structure_definitions=(
                FIELDED_MODEL_STRUCTURE_DEFINITIONS
            ),
            profiles_by_id=profiles_by_id,
        )
    )

    fielded_model_form_states = (
        get_initial_fielded_model_form_states(
            army=army,
            allowed_alternates_by_profile_id=(
                ALLOWED_ALTERNATE_FORMS_BY_PROFILE_ID
            ),
            fielded_models=fielded_models,
        )
    )

    leader_profile = None
    leader_model = None

    leader_profile_id = getattr(
        definition,
        "leader_profile_id",
        None,
    )

    if leader_profile_id is not None:
        leader_profile = profiles_by_id[
            leader_profile_id
        ]

        leader_warband_id = getattr(
            definition,
            "leader_warband_id",
            None,
        )

        leader_model = next(
            (
                fielded_model
                for fielded_model in fielded_models
                if (
                    fielded_model.profile_id
                    == leader_profile_id
                    and (
                        leader_warband_id is None
                        or fielded_model.warband_id
                        == leader_warband_id
                    )
                )
            ),
            None,
        )

    if key_profile is None:
            key_profile = leader_profile

    analysis_points_limit = (
        definition.points_limit
        if definition.points_limit is not None
        else army.total_points()
    )

    default_scenario_context = (
        build_default_scenario_analysis_context(
            points_limit=analysis_points_limit,
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
                leader_model=leader_model,
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
        "fielded_model_structures": (
            fielded_model_structures
        ),
        "fielded_model_form_states": (
            fielded_model_form_states
        ),
        "analysis": analysis_result,
        "scenario_analysis_results": (
            scenario_analysis_results
        ),
    }