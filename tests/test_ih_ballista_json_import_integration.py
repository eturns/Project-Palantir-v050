from pathlib import Path

from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from loader import load_all_profiles
from army_loader import (
    load_factions,
    load_army_lists,
    load_army_list_profiles,
)
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)
from siege_engine_profile_loader import (
    load_siege_engine_profiles,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from fielded_model_structure_builder import (
    build_fielded_model_structures,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from importers.mesbg_list_builder_fielded_structure_map import (
    FIELDED_MODEL_STRUCTURE_DEFINITIONS,
)
from analysis_loader import load_metric_thresholds
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)

FIXTURE_PATH = (
    Path("tests")
    / "fixtures"
    / "ih_ballista.json"
)


def get_entry(
    definition,
    profile_id: str,
    external_option_ids: tuple[str, ...] = (),
):
    return next(
        entry
        for entry in definition.entries
        if (
            entry.profile_id == profile_id
            and entry.external_option_ids
            == external_option_ids
        )
    )


def test_real_ih_ballista_json_expands_composite_structure():
    definition = import_army_definition_from_json(
        str(FIXTURE_PATH)
    )

    assert definition.army_list_id == (
        "IH_IRON_HILLS"
    )

    assert definition.points_limit is None

    assert definition.leader_profile_id == (
        "IH_DAIN"
    )

    ballista = get_entry(
        definition,
        "IH_BALLISTA",
    )

    normal_crew = get_entry(
        definition,
        "IH_SIEGE_CREW",
    )

    veteran = get_entry(
        definition,
        "IH_SIEGE_CREW",
        ("IH_SIEGE_VETERAN",),
    )

    assert ballista.quantity == 1

    assert normal_crew.quantity == 3

    assert veteran.quantity == 1

    assert (
        ballista.warband_id
        == normal_crew.warband_id
        == veteran.warband_id
        == "e70890ec-72a9-42c6-9230-eced3fda5430"
    )

def test_real_ih_ballista_json_builds_runtime_army():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    profile_options = load_profile_options(
        profiles_by_id,
    )

    load_profile_option_state_effects(
        profile_options,
    )

    profile_options_by_external_id = (
        build_profile_options_by_external_id(
            profile_options
        )
    )

    siege_engine_profiles_by_id = (
        load_siege_engine_profiles()
    )

    factions = load_factions()

    army_lists = load_army_lists(
        factions
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            str(FIXTURE_PATH),
            profiles_by_id,
            army_lists,
            profile_options_by_external_id=(
                profile_options_by_external_id
            ),
            siege_engine_profiles_by_id=(
                siege_engine_profiles_by_id
            ),
        )
    )

    assert definition.army_list_id == (
        "IH_IRON_HILLS"
    )

    assert army_list.id == (
        "IH_IRON_HILLS"
    )

    assert army.total_points() == 290

    assert army.model_count() == 5

    fielded_models = army.fielded_models()

    crew_models = [
        model
        for model in fielded_models
        if model.profile_id == "IH_SIEGE_CREW"
    ]

    assert len(crew_models) == 4

    veterans = [
        model
        for model in crew_models
        if (
            model.configured_profile.effective_might == 1
            and model.configured_profile.effective_will == 1
            and model.configured_profile.effective_fate == 1
        )
    ]

    assert len(veterans) == 1

    veteran = veterans[0]

    assert (
        veteran.configured_profile.effective_heroic_status.name
        == "HERO"
    )

    ordinary_crew = [
        model
        for model in crew_models
        if model is not veteran
    ]

    assert len(ordinary_crew) == 3

    assert all(
        model.configured_profile.effective_might == 0
        for model in ordinary_crew
    )

    ballista = next(
        model
        for model in fielded_models
        if model.profile_id == "IH_BALLISTA"
    )

    assert ballista.counts_as_model is False

    assert len(fielded_models) == 6

    assert len({
        model.id
        for model in fielded_models
    }) == 6

    profile_ids = [
        model.profile_id
        for model in fielded_models
    ]

    assert profile_ids.count(
        "IH_BALLISTA"
    ) == 1

    assert profile_ids.count(
        "IH_SIEGE_CREW"
    ) == 4

    assert profile_ids.count(
        "IH_DAIN"
    ) == 1

    structures = build_fielded_model_structures(
        fielded_models=fielded_models,
        structure_definitions=(
            FIELDED_MODEL_STRUCTURE_DEFINITIONS
        ),
        profiles_by_id=profiles_by_id,
    )

    crew_relationships = [
        relationship
        for relationship in structures.relationships
        if (
            relationship.relationship_type
            is FieldedModelRelationshipType.CREW_OF
        )
    ]

    assert len(crew_relationships) == 4

    assert {
        relationship.source_fielded_model_id
        for relationship in crew_relationships
    } == {
        model.id
        for model in crew_models
    }

    assert {
        relationship.target_fielded_model_id
        for relationship in crew_relationships
    } == {
        ballista.id
    }

def test_real_ih_ballista_json_runs_shared_analysis_with_structures():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    profile_options = load_profile_options(
        profiles_by_id,
    )

    load_profile_option_state_effects(
        profile_options,
    )

    profile_options_by_external_id = (
        build_profile_options_by_external_id(
            profile_options
        )
    )

    siege_engine_profiles_by_id = (
        load_siege_engine_profiles()
    )

    factions = load_factions()

    army_lists = load_army_lists(
        factions
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    metric_thresholds = (
        load_metric_thresholds()
    )

    result = analyse_mesbg_list_builder_file(
        str(FIXTURE_PATH),
        profiles_by_id,
        army_lists,
        metric_thresholds,
        profile_options_by_external_id=(
            profile_options_by_external_id
        ),
        siege_engine_profiles_by_id=(
            siege_engine_profiles_by_id
        ),
    )

    assert result["army"].total_points() == 290
    assert result["army"].model_count() == 5

    structures = result["fielded_model_structures"]

    crew_relationships = [
        relationship
        for relationship in structures.relationships
        if (
            relationship.relationship_type
            is FieldedModelRelationshipType.CREW_OF
        )
    ]

    assert len(crew_relationships) == 4

    assert result["analysis"] is not None

    assert (
        result["scenario_analysis_results"]
        is not None
    )