from pathlib import Path

from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from army_builder import build_army_from_definition
from army_loader import (
    load_factions,
    load_army_lists,
)
from loader import load_all_profiles
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from siege_engine_profile_loader import (
    load_siege_engine_profiles,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_builder import (
    build_fielded_model_structures,
)
from importers.mesbg_list_builder_fielded_structure_map import (
    FIELDED_MODEL_STRUCTURE_DEFINITIONS,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from analysis_loader import load_metric_thresholds
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)

FIXTURE_PATH = (
    Path("tests")
    / "fixtures"
    / "bard_family.json"
)


def test_real_bard_family_json_expands_grouped_purchase():
    definition = import_army_definition_from_json(
        str(FIXTURE_PATH)
    )

    assert definition.army_list_id == "LAKE_TOWN"
    assert definition.points_limit is None

    assert len(definition.purchases) == 1

    purchase = definition.purchases[0]

    assert purchase.points == 60
    assert purchase.quantity == 1

    profile_ids = [
        entry.profile_id
        for entry in definition.entries
    ]

    assert profile_ids.count("BARD") == 1
    assert profile_ids.count("BAIN") == 1
    assert profile_ids.count("SIGRID") == 1
    assert profile_ids.count("TILDA") == 1

    bard_entry = next(
        entry
        for entry in definition.entries
        if entry.profile_id == "BARD"
    )

    assert bard_entry.external_option_ids == (
        "OPT0735",
    )

    family_entries = [
        entry
        for entry in definition.entries
        if entry.profile_id in {
            "BAIN",
            "SIGRID",
            "TILDA",
        }
    ]

    assert len(family_entries) == 3

    assert all(
        entry.quantity == 1
        for entry in family_entries
    )

    assert len({
        entry.warband_id
        for entry in family_entries
    }) == 1

def test_real_bard_family_json_builds_runtime_army_with_windlance():
    definition = import_army_definition_from_json(
        str(FIXTURE_PATH)
    )

    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            options
        )
    )

    siege_engine_profiles = (
        load_siege_engine_profiles()
    )

    factions = load_factions()

    army_lists = load_army_lists(
        factions
    )

    army, army_list = build_army_from_definition(
        definition,
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
        siege_engine_profiles_by_id=(
            siege_engine_profiles
        ),
    )

    assert army_list.id == "LAKE_TOWN"

    assert army.total_points() == 240
    assert army.model_count() == 4

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 5

    profile_ids = [
        model.profile_id
        for model in fielded_models
    ]

    assert profile_ids.count("BARD") == 1
    assert profile_ids.count("BAIN") == 1
    assert profile_ids.count("SIGRID") == 1
    assert profile_ids.count("TILDA") == 1
    assert profile_ids.count("DALE_WINDLANCE") == 1

    bard = next(
        model
        for model in fielded_models
        if model.profile_id == "BARD"
    )

    assert bard.configured_profile is not None

    assert {
        option.id
        for option
        in bard.configured_profile.selected_options
    } == {
        "BARD_WINDLANCE",
    }

    windlance = next(
        model
        for model in fielded_models
        if model.profile_id == "DALE_WINDLANCE"
    )

    assert (
        windlance.warband_id
        == bard.warband_id
    )

    family = tuple(
        model
        for model in fielded_models
        if model.profile_id in {
            "BAIN",
            "SIGRID",
            "TILDA",
        }
    )

    assert len(family) == 3

    assert all(
        model.warband_id == bard.warband_id
        for model in family
    )

    relationships = build_fielded_model_structures(
        fielded_models=fielded_models,
        structure_definitions=(
            FIELDED_MODEL_STRUCTURE_DEFINITIONS
        ),
        profiles_by_id=profiles,
    )

    crew_relationships = tuple(
        relationship
        for relationship in relationships.relationships
        if (
            relationship.relationship_type
            is FieldedModelRelationshipType.CREW_OF
        )
    )

    assert len(crew_relationships) == 1

    crew_relationship = crew_relationships[0]

    assert (
        crew_relationship.source_fielded_model_id
        == bard.id
    )

    assert (
        crew_relationship.target_fielded_model_id
        == windlance.id
    )

def test_real_bard_family_json_survives_shared_import_service():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            options
        )
    )

    siege_engine_profiles = (
        load_siege_engine_profiles()
    )

    factions = load_factions()
    army_lists = load_army_lists(
        factions
    )

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            str(FIXTURE_PATH),
            profiles_by_id=profiles,
            army_lists_by_id=army_lists,
            profile_options_by_external_id=(
                options_by_external_id
            ),
            siege_engine_profiles_by_id=(
                siege_engine_profiles
            ),
        )
    )

    assert definition.army_list_id == "LAKE_TOWN"
    assert army_list.id == "LAKE_TOWN"

    assert army.total_points() == 240
    assert army.model_count() == 4

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 5

    assert {
        model.profile_id
        for model in fielded_models
    } == {
        "BARD",
        "BAIN",
        "SIGRID",
        "TILDA",
        "DALE_WINDLANCE",
    }

def test_real_bard_family_json_survives_shared_analysis_service():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            options
        )
    )

    siege_engine_profiles = (
        load_siege_engine_profiles()
    )

    factions = load_factions()
    army_lists = load_army_lists(
        factions
    )

    metric_thresholds = load_metric_thresholds()

    result = analyse_mesbg_list_builder_file(
        str(FIXTURE_PATH),
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        metric_thresholds=metric_thresholds,
        profile_options_by_external_id=(
            options_by_external_id
        ),
        siege_engine_profiles_by_id=(
            siege_engine_profiles
        ),
    )

    army = result["army"]

    assert army.total_points() == 240
    assert army.model_count() == 4

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 5

    assert {
        model.profile_id
        for model in fielded_models
    } == {
        "BARD",
        "BAIN",
        "SIGRID",
        "TILDA",
        "DALE_WINDLANCE",
    }

    relationships = (
        result["fielded_model_structures"]
    )

    assert len(
        relationships.relationships
    ) == 1

    relationship = (
        relationships.relationships[0]
    )

    bard = next(
        model
        for model in fielded_models
        if model.profile_id == "BARD"
    )

    windlance = next(
        model
        for model in fielded_models
        if model.profile_id == "DALE_WINDLANCE"
    )

    assert (
        relationship.source_fielded_model_id
        == bard.id
    )

    assert (
        relationship.target_fielded_model_id
        == windlance.id
    )

    assert (
        relationship.relationship_type
        is FieldedModelRelationshipType.CREW_OF
    )