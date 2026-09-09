from pathlib import Path

import main as main_module

from profile_option import ProfileOption
from profiles import Profile


def create_profile() -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_main_passes_external_option_lookup_to_analysis_service(
    monkeypatch,
    tmp_path,
):
    army_file = tmp_path / "army.json"
    army_file.write_text(
        "{}",
        encoding="utf-8",
    )

    profile = create_profile()

    option = ProfileOption(
        id="INTERNAL_OPTION",
        name="Configured Option",
        points=10,
        external_id="EXT_OPTION",
    )

    captured = {}

    profile_options = {
        option.id: option,
    }

    profile_options_by_external_id = {
        "EXT_OPTION": option,
    }

    monkeypatch.setattr(
        main_module,
        "load_all_profiles",
        lambda: [profile],
    )

    monkeypatch.setattr(
        main_module,
        "load_factions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_lists",
        lambda factions: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rules",
        lambda army_lists: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rules",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_actions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_spells",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_tags",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_prerequisites",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_thresholds",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_descriptions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_special_rules",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_heroic_actions",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_spells",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "total_points",
        lambda profiles: 20,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_options",
        lambda profiles_by_id: profile_options,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "build_profile_options_by_external_id",
        lambda options: profile_options_by_external_id,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_platforms",
        lambda: {},
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_platform_assignments",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_state_effects",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_special_rules",
        lambda *args, **kwargs: None,
        raising=False,
    )

    def fake_analysis(
        file_path,
        profiles_by_id,
        army_lists_by_id,
        metric_thresholds,
        *,
        profile_options_by_external_id=None,
        **kwargs,
    ):
        captured["options"] = (
            profile_options_by_external_id
        )

        return {
            "definition": object(),
            "army": object(),
            "army_list": object(),
            "analysis": object(),
            "scenario_analysis_results": None,
        }

    monkeypatch.setattr(
        main_module,
        "load_wargear",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_wargear_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "analyse_mesbg_list_builder_file",
        fake_analysis,
    )

    monkeypatch.setattr(
        main_module,
        "print_text_analysis_report",
        lambda result: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_mounts",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_mount_assignments",
        lambda *args, **kwargs: None,
    )

    main_module.main(
        str(army_file),
    )

    assert captured["options"] is not None

    assert (
        captured["options"]["EXT_OPTION"]
        is option
    )

def test_main_loads_profile_option_mount_relationships(
    monkeypatch,
    tmp_path,
):
    army_file = tmp_path / "army.json"
    army_file.write_text(
        "{}",
        encoding="utf-8",
    )

    profile = create_profile()

    profile_options = {}
    mounts = {}

    calls = []

    monkeypatch.setattr(
        main_module,
        "load_all_profiles",
        lambda: [profile],
    )

    monkeypatch.setattr(
        main_module,
        "load_factions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_lists",
        lambda factions: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rules",
        lambda army_lists: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rules",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_actions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_spells",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_tags",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_prerequisites",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_thresholds",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_descriptions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_special_rules",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_heroic_actions",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_spells",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "total_points",
        lambda profiles: 20,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_options",
        lambda profiles_by_id: profile_options,
    )

    monkeypatch.setattr(
        main_module,
        "build_profile_options_by_external_id",
        lambda options: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_mounts",
        lambda: mounts,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_platforms",
        lambda: {},
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_platform_assignments",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_state_effects",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_special_rules",
        lambda *args, **kwargs: None,
        raising=False,
    )

    def fake_load_option_mounts(
        profile_options,
        mounts,
    ):
        calls.append(
            (
                profile_options,
                mounts,
            )
        )

    monkeypatch.setattr(
        main_module,
        "load_wargear",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_wargear_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_mount_assignments",
        fake_load_option_mounts,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "analyse_mesbg_list_builder_file",
        lambda *args, **kwargs: {},
    )

    monkeypatch.setattr(
        main_module,
        "print_text_analysis_report",
        lambda result: None,
    )

    main_module.main(
        str(army_file),
    )

    assert calls == [
        (
            profile_options,
            mounts,
        )
    ]

def test_main_loads_profile_option_wargear_relationships(
    monkeypatch,
    tmp_path,
):
    army_file = tmp_path / "army.json"
    army_file.write_text(
        "{}",
        encoding="utf-8",
    )

    profile = create_profile()

    profile_options = {}
    wargear = {}

    calls = []

    monkeypatch.setattr(
        main_module,
        "load_all_profiles",
        lambda: [profile],
    )

    monkeypatch.setattr(
        main_module,
        "load_factions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_lists",
        lambda factions: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rules",
        lambda army_lists: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rules",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_actions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_spells",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_tags",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_prerequisites",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_thresholds",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_descriptions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_special_rules",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_heroic_actions",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_spells",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "total_points",
        lambda profiles: 20,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_options",
        lambda profiles_by_id: profile_options,
    )

    monkeypatch.setattr(
        main_module,
        "build_profile_options_by_external_id",
        lambda options: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_mounts",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_mount_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_wargear",
        lambda: wargear,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_platforms",
        lambda: {},
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_platform_assignments",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_state_effects",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_special_rules",
        lambda *args, **kwargs: None,
        raising=False,
    )

    def fake_load_option_wargear(
        profile_options,
        wargear,
    ):
        calls.append(
            (
                profile_options,
                wargear,
            )
        )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_wargear_assignments",
        fake_load_option_wargear,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "analyse_mesbg_list_builder_file",
        lambda *args, **kwargs: {},
    )

    monkeypatch.setattr(
        main_module,
        "print_text_analysis_report",
        lambda result: None,
    )

    main_module.main(
        str(army_file),
    )

    assert calls == [
        (
            profile_options,
            wargear,
        )
    ]

def test_main_loads_profile_option_platform_relationships(
    monkeypatch,
    tmp_path,
):
    army_file = tmp_path / "army.json"
    army_file.write_text(
        "{}",
        encoding="utf-8",
    )

    profile = create_profile()

    profile_options = {}
    platforms = {}

    calls = []

    monkeypatch.setattr(
        main_module,
        "load_all_profiles",
        lambda: [profile],
    )

    monkeypatch.setattr(
        main_module,
        "load_factions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_lists",
        lambda factions: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rules",
        lambda army_lists: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rules",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_actions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_spells",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_tags",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_prerequisites",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_thresholds",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_descriptions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_special_rules",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_heroic_actions",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_spells",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "total_points",
        lambda profiles: 20,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_options",
        lambda profiles_by_id: profile_options,
    )

    monkeypatch.setattr(
        main_module,
        "build_profile_options_by_external_id",
        lambda options: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_mounts",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_mount_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_wargear",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_wargear_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_platforms",
        lambda: platforms,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_state_effects",
        lambda *args, **kwargs: None,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_special_rules",
        lambda *args, **kwargs: None,
        raising=False,
    )

    def fake_load_option_platforms(
        profile_options,
        platforms,
    ):
        calls.append(
            (
                profile_options,
                platforms,
            )
        )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_platform_assignments",
        fake_load_option_platforms,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "analyse_mesbg_list_builder_file",
        lambda *args, **kwargs: {},
    )

    monkeypatch.setattr(
        main_module,
        "print_text_analysis_report",
        lambda result: None,
    )

    main_module.main(
        str(army_file),
    )

    assert calls == [
        (
            profile_options,
            platforms,
        )
    ]

def test_main_loads_profile_option_state_effects(
    monkeypatch,
    tmp_path,
):
    army_file = tmp_path / "army.json"
    army_file.write_text(
        "{}",
        encoding="utf-8",
    )

    profile = create_profile()

    profile_options = {}

    calls = []

    monkeypatch.setattr(
        main_module,
        "load_all_profiles",
        lambda: [profile],
    )

    monkeypatch.setattr(
        main_module,
        "load_factions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_lists",
        lambda factions: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rules",
        lambda army_lists: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rules",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_actions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_spells",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_tags",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_prerequisites",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_thresholds",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_descriptions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_special_rules",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_heroic_actions",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_spells",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "total_points",
        lambda profiles: 20,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_options",
        lambda profiles_by_id: profile_options,
    )

    monkeypatch.setattr(
        main_module,
        "build_profile_options_by_external_id",
        lambda options: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_mounts",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_mount_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_wargear",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_wargear_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_platforms",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_platform_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_special_rules",
        lambda *args, **kwargs: None,
        raising=False,
    )
    
    def fake_load_state_effects(
        profile_options,
    ):
        calls.append(profile_options)

    monkeypatch.setattr(
        main_module,
        "load_profile_option_state_effects",
        fake_load_state_effects,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "analyse_mesbg_list_builder_file",
        lambda *args, **kwargs: {},
    )

    monkeypatch.setattr(
        main_module,
        "print_text_analysis_report",
        lambda result: None,
    )

    main_module.main(
        str(army_file),
    )

    assert calls == [
        profile_options,
    ]

def test_main_loads_profile_option_special_rule_effects(
    monkeypatch,
    tmp_path,
):
    army_file = tmp_path / "army.json"
    army_file.write_text(
        "{}",
        encoding="utf-8",
    )

    profile = create_profile()

    profile_options = {}
    special_rules = {}

    calls = []

    monkeypatch.setattr(
        main_module,
        "load_all_profiles",
        lambda: [profile],
    )

    monkeypatch.setattr(
        main_module,
        "load_factions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_lists",
        lambda factions: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rules",
        lambda army_lists: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rules",
        lambda: special_rules,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_actions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_spells",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_tags",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_ability_prerequisites",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_thresholds",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_metric_descriptions",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_special_rules",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_heroic_actions",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_spells",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_army_rule_tags",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_heroic_action_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_spell_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_special_rule_prerequisites",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "total_points",
        lambda profiles: 20,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_options",
        lambda profiles_by_id: profile_options,
    )

    monkeypatch.setattr(
        main_module,
        "build_profile_options_by_external_id",
        lambda options: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_mounts",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_mount_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_wargear",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_wargear_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_platforms",
        lambda: {},
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_platform_assignments",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_state_effects",
        lambda *args, **kwargs: None,
    )

    def fake_load_option_special_rules(
        profile_options,
        special_rules,
    ):
        calls.append(
            (
                profile_options,
                special_rules,
            )
        )

    monkeypatch.setattr(
        main_module,
        "load_profile_option_special_rules",
        fake_load_option_special_rules,
        raising=False,
    )

    monkeypatch.setattr(
        main_module,
        "analyse_mesbg_list_builder_file",
        lambda *args, **kwargs: {},
    )

    monkeypatch.setattr(
        main_module,
        "print_text_analysis_report",
        lambda result: None,
    )

    main_module.main(
        str(army_file),
    )

    assert calls == [
        (
            profile_options,
            special_rules,
        )
    ]