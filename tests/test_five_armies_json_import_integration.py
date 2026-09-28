from pathlib import Path

from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from loader import load_all_profiles
from army_loader import load_factions, load_army_lists
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from wargear_loader import load_wargear
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from mount_loader import load_mounts
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from analysis_loader import load_metric_thresholds
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "five_armies.json"
)


def test_five_armies_real_json_imports_army_definition():
    definition = import_army_definition_from_json(
        str(FIXTURE_PATH)
    )

    assert definition.army_list_id == "BATTLE_OF_FIVE_ARMIES"
    assert len(definition.entries) == 4

    assert sum(
        entry.quantity
        for entry in definition.entries
    ) == 6

def test_five_armies_real_json_builds_runtime_army():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_option_wargear_assignments(
        options,
        load_wargear(),
    )

    load_profile_option_mount_assignments(
        options,
        load_mounts(),
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            options
        )
    )

    army_lists = load_army_lists(
        load_factions()
    )

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            str(FIXTURE_PATH),
            profiles_by_id=profiles,
            army_lists_by_id=army_lists,
            profile_options_by_external_id=(
                options_by_external_id
            ),
        )
    )

    assert definition.army_list_id == (
        "BATTLE_OF_FIVE_ARMIES"
    )
    assert army_list.id == "BATTLE_OF_FIVE_ARMIES"

    assert army.total_points() == 346
    assert army.model_count() == 6

    dain_warband = next(
        entry.warband_id
        for entry in army.entries
        if entry.profile.id == "IH_DAIN"
    )

    bard_warband = next(
        entry.warband_id
        for entry in army.entries
        if entry.profile.id == "BARD"
    )

    assert dain_warband != bard_warband

    warriors = next(
        entry
        for entry in army.entries
        if entry.profile.id == "IH_WR"
    )

    militia = next(
        entry
        for entry in army.entries
        if entry.profile.id == "LAKE_TOWN_MILITIA"
    )

    assert warriors.quantity == 2
    assert warriors.warband_id == dain_warband

    assert militia.quantity == 2
    assert militia.warband_id == bard_warband

    assert {
        item.id
        for item in warriors.configured_profile.effective_wargear
    } >= {"WG_SHIELD", "WG_SPEAR"}

    assert "WG_SPEAR" in {
        item.id
        for item in militia.configured_profile.effective_wargear
    }

    bard = next(
        entry
        for entry in army.entries
        if entry.profile.id == "BARD"
    )

    bard_wargear = {
        item.id
        for item in bard.configured_profile.effective_wargear
    }

    assert "WG_ARMOUR" in bard_wargear
    assert "WG_GREAT_BOW" not in bard_wargear

    assert (
        bard.configured_profile.effective_mount.id
        == "MOUNT_HORSE"
    )

    assert bard.configured_profile.effective_base_size_mm == 40
    assert bard.configured_profile.points == 150

def test_five_armies_real_json_runs_shared_analysis():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_option_wargear_assignments(
        options,
        load_wargear(),
    )

    load_profile_option_mount_assignments(
        options,
        load_mounts(),
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            options
        )
    )

    army_lists = load_army_lists(
        load_factions()
    )

    result = analyse_mesbg_list_builder_file(
        str(FIXTURE_PATH),
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    assert result["definition"].army_list_id == (
        "BATTLE_OF_FIVE_ARMIES"
    )
    assert result["army"].total_points() == 346
    assert result["army"].model_count() == 6

    assert result["analysis"] is not None
    assert result["analysis"]["validation_errors"] == []

    assert result["scenario_analysis_results"] is not None
    assert len(result["scenario_analysis_results"]) == 24