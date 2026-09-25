import json
from pathlib import Path
from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)
from loader import load_all_profiles
from army_loader import (
    load_factions,
    load_army_lists,
    load_army_list_profiles,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from analysis_loader import load_metric_thresholds
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "garrison_of_dale.json"
)

def test_garrison_of_dale_import_preserves_roster_structure():
    data = json.loads(
        FIXTURE_PATH.read_text(
            encoding="utf-8"
        )
    )

    army = build_army_definition_from_data(
        data
    )

    assert army.army_list_id == "GARRISON_OF_DALE"

    assert army.leader_warband_id == (
        "c495f6e4-7b60-447c-8ff7-9e024c04069e"
    )
    assert army.leader_profile_id == "DALE_GIRION"
    assert army.leader_compulsory is True

    assert len(army.entries) == 4

    entries = {
        (
            entry.profile_id,
            entry.warband_id,
        ): entry
        for entry in army.entries
    }

    girion = entries[
        (
            "DALE_GIRION",
            "c495f6e4-7b60-447c-8ff7-9e024c04069e",
        )
    ]

    assert girion.quantity == 1
    assert girion.is_warband_leader is True
    assert girion.is_compulsory is True

    girion_warriors = entries[
        (
            "DALE_WARRIOR",
            "c495f6e4-7b60-447c-8ff7-9e024c04069e",
        )
    ]

    assert girion_warriors.quantity == 3
    assert girion_warriors.is_warband_leader is False
    assert girion_warriors.is_compulsory is False

    captain = entries[
        (
            "DALE_CAPTAIN",
            "082d075c-2f99-4222-b842-93525d940ac8",
        )
    ]

    assert captain.quantity == 1
    assert captain.is_warband_leader is True
    assert captain.is_compulsory is False

    captain_warriors = entries[
        (
            "DALE_WARRIOR",
            "082d075c-2f99-4222-b842-93525d940ac8",
        )
    ]

    assert captain_warriors.quantity == 3
    assert captain_warriors.is_warband_leader is False
    assert captain_warriors.is_compulsory is False

def test_garrison_of_dale_real_json_builds_runtime_army():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

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
        )
    )

    assert definition.army_list_id == (
        "GARRISON_OF_DALE"
    )

    assert army_list.id == (
        "GARRISON_OF_DALE"
    )

    assert army.total_points() == 177

    assert army.model_count() == 8

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 8

    assert len({
        model.id
        for model in fielded_models
    }) == 8

    profile_counts = {}

    for model in fielded_models:
        profile_counts[model.profile_id] = (
            profile_counts.get(
                model.profile_id,
                0,
            )
            + 1
        )

    assert profile_counts == {
        "DALE_GIRION": 1,
        "DALE_CAPTAIN": 1,
        "DALE_WARRIOR": 6,
    }

    girion_warband = (
        "c495f6e4-7b60-447c-8ff7-9e024c04069e"
    )

    captain_warband = (
        "082d075c-2f99-4222-b842-93525d940ac8"
    )

    assert {
        model.profile_id
        for model in fielded_models
        if model.warband_id == girion_warband
    } == {
        "DALE_GIRION",
        "DALE_WARRIOR",
    }

    assert {
        model.profile_id
        for model in fielded_models
        if model.warband_id == captain_warband
    } == {
        "DALE_CAPTAIN",
        "DALE_WARRIOR",
    }

    assert sum(
        1
        for model in fielded_models
        if model.warband_id == girion_warband
    ) == 4

    assert sum(
        1
        for model in fielded_models
        if model.warband_id == captain_warband
    ) == 4

def test_garrison_of_dale_real_json_runs_shared_analysis_path():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

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
    )

    assert result["definition"].army_list_id == (
        "GARRISON_OF_DALE"
    )

    assert result["army_list"].id == (
        "GARRISON_OF_DALE"
    )

    assert result["army"].total_points() == 177

    assert result["army"].model_count() == 8

    assert result["analysis"] is not None

    assert (
        result["analysis"]["validation_errors"]
        == []
    )

    assert (
        result["scenario_analysis_results"]
        is not None
    )