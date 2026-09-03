from services import mesbg_list_analysis_service
from types import SimpleNamespace
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)
from pathlib import Path

import pytest

from analysis_loader import load_metric_thresholds
from army_loader import (
    load_army_lists,
    load_army_rules,
    load_factions,
)
from loader import load_all_profiles
from relationship_loader import (
    load_army_rule_tags,
    load_heroic_action_prerequisites,
    load_heroic_action_tags,
    load_profile_heroic_actions,
    load_profile_special_rules,
    load_profile_spells,
    load_special_rule_prerequisites,
    load_special_rule_tags,
    load_spell_prerequisites,
    load_spell_tags,
)
from rule_loader import (
    load_ability_prerequisites,
    load_ability_tags,
    load_heroic_actions,
    load_special_rules,
    load_spells,
)
from scenario_demand import StrategicDemand

def test_mesbg_list_analysis_service_returns_scenario_analysis_results(
    monkeypatch,
):
    definition = SimpleNamespace(
    points_limit=777,
)
    army = object()
    army_list = object()
    analysis_result = object()

    scenario_results = (
        "SCENARIO_RESULT_1",
        "SCENARIO_RESULT_2",
    )

    monkeypatch.setattr(
        mesbg_list_analysis_service,
        "import_army_from_mesbg_list_builder",
        lambda *args, **kwargs: (
            definition,
            army,
            army_list,
        ),
    )

    monkeypatch.setattr(
        mesbg_list_analysis_service,
        "analyse_imported_army",
        lambda *args, **kwargs: analysis_result,
    )

    monkeypatch.setattr(
        mesbg_list_analysis_service,
        "build_scenario_analysis_results_from_candidate",
        lambda **kwargs: scenario_results,
        raising=False,
    )

    result = (
        mesbg_list_analysis_service.analyse_mesbg_list_builder_file(
            "army.json",
            {},
            {},
            {},
            key_profile="KEY_PROFILE",
            combat_benchmark="COMBAT_BENCHMARK",
            benchmark_presence=10.0,
            benchmark_manoeuvrability=1.0,
            benchmark_combat_capability=0.5,
            benchmark_fate=4.0,
        )
    )

    assert result["definition"] is definition
    assert result["army"] is army
    assert result["army_list"] is army_list
    assert result["analysis"] is analysis_result

    assert result["scenario_analysis_results"] == (
        scenario_results
    )

def test_analysis_service_passes_imported_leader_profile_to_scenario_builder(
    monkeypatch,
):
    leader_profile = object()

    definition = SimpleNamespace(
        points_limit=777,
        leader_profile_id="LEADER_PROFILE",
    )

    army = object()
    army_list = object()

    captured = {}

    def fake_import(
        file_path,
        profiles_by_id,
        army_lists_by_id,
    ):
        return (
            definition,
            army,
            army_list,
        )

    def fake_army_analysis(
        army,
        army_list,
        points_limit,
        metric_thresholds,
    ):
        return "ANALYSIS"

    def fake_scenario_builder(
        **kwargs,
    ):
        captured.update(kwargs)

        return (
            "SCENARIO_RESULT",
        )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "import_army_from_mesbg_list_builder",
        fake_import,
    )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "analyse_imported_army",
        fake_army_analysis,
    )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "build_scenario_analysis_results_from_candidate",
        fake_scenario_builder,
    )

    result = analyse_mesbg_list_builder_file(
        "army.json",
        profiles_by_id={
            "LEADER_PROFILE": leader_profile,
        },
        army_lists_by_id={},
        metric_thresholds="THRESHOLDS",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    assert result["scenario_analysis_results"] == (
        "SCENARIO_RESULT",
    )

    assert captured["leader_profile"] is leader_profile

    assert captured["preservation_profile"] is leader_profile

def test_analysis_service_builds_default_scenario_context_when_not_supplied(
    monkeypatch,
):
    leader_profile = object()

    definition = SimpleNamespace(
        points_limit=350,
        leader_profile_id="LEADER_PROFILE",
    )

    army = object()
    army_list = object()

    captured = {}

    def fake_import(
        file_path,
        profiles_by_id,
        army_lists_by_id,
    ):
        return (
            definition,
            army,
            army_list,
        )

    def fake_army_analysis(
        army,
        army_list,
        points_limit,
        metric_thresholds,
    ):
        return "ANALYSIS"

    def fake_scenario_builder(
        **kwargs,
    ):
        captured.update(kwargs)

        return (
            "SCENARIO_RESULT",
        )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "import_army_from_mesbg_list_builder",
        fake_import,
    )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "analyse_imported_army",
        fake_army_analysis,
    )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "build_scenario_analysis_results_from_candidate",
        fake_scenario_builder,
    )

    result = analyse_mesbg_list_builder_file(
        "army.json",
        profiles_by_id={
            "LEADER_PROFILE": leader_profile,
        },
        army_lists_by_id={},
        metric_thresholds="THRESHOLDS",
        key_profile="KEY_PROFILE",
    )

    assert result["scenario_analysis_results"] == (
        "SCENARIO_RESULT",
    )

    assert captured["benchmark_presence"] == 5.0
    assert captured["benchmark_manoeuvrability"] == 6.0
    assert captured["benchmark_combat_capability"] == 0.5
    assert captured["benchmark_fate"] == 3.0

def test_analysis_service_runs_scenario_analysis_without_manual_context(
    monkeypatch,
):
    leader_profile = object()

    definition = SimpleNamespace(
        points_limit=700,
        leader_profile_id="LEADER_PROFILE",
    )

    army = object()
    army_list = object()

    captured = {}

    def fake_import(
        file_path,
        profiles_by_id,
        army_lists_by_id,
    ):
        return (
            definition,
            army,
            army_list,
        )

    def fake_army_analysis(
        army,
        army_list,
        points_limit,
        metric_thresholds,
    ):
        return "ANALYSIS"

    def fake_scenario_builder(
        **kwargs,
    ):
        captured.update(kwargs)

        return (
            "SCENARIO_RESULT",
        )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "import_army_from_mesbg_list_builder",
        fake_import,
    )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "analyse_imported_army",
        fake_army_analysis,
    )

    monkeypatch.setattr(
        "services.mesbg_list_analysis_service."
        "build_scenario_analysis_results_from_candidate",
        fake_scenario_builder,
    )

    result = analyse_mesbg_list_builder_file(
        "army.json",
        profiles_by_id={
            "LEADER_PROFILE": leader_profile,
        },
        army_lists_by_id={},
        metric_thresholds="THRESHOLDS",
    )

    assert result["scenario_analysis_results"] == (
        "SCENARIO_RESULT",
    )

    assert captured["key_profile"] is leader_profile
    assert captured["leader_profile"] is leader_profile
    assert captured["preservation_profile"] is leader_profile

def test_real_eddies_choice_matches_main_scenario_pipeline():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    army_rules = load_army_rules(
        army_lists,
    )

    special_rules = load_special_rules()
    heroic_actions = load_heroic_actions()
    spells = load_spells()
    ability_tags = load_ability_tags()
    ability_prerequisites = (
        load_ability_prerequisites()
    )

    metric_thresholds = load_metric_thresholds()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    load_profile_heroic_actions(
        profiles_by_id,
        heroic_actions,
    )

    load_profile_spells(
        profiles_by_id,
        spells,
    )

    load_special_rule_tags(
        special_rules,
        ability_tags,
    )

    load_heroic_action_tags(
        heroic_actions,
        ability_tags,
    )

    load_spell_tags(
        spells,
        ability_tags,
    )

    load_army_rule_tags(
        army_rules,
        ability_tags,
    )

    load_heroic_action_prerequisites(
        heroic_actions,
        ability_prerequisites,
    )

    load_spell_prerequisites(
        spells,
        ability_prerequisites,
    )

    load_special_rule_prerequisites(
        special_rules,
        ability_prerequisites,
    )

    result = analyse_mesbg_list_builder_file(
        str(
            Path("src")
            / "eddies-choice.json"
        ),
        profiles_by_id,
        army_lists,
        metric_thresholds,
    )

    scenario_results = (
        result["scenario_analysis_results"]
    )

    assert scenario_results is not None
    assert len(scenario_results) == 24

    lead_from_the_front = next(
        scenario
        for scenario in scenario_results
        if scenario.scenario_id
        == "LEAD_FROM_THE_FRONT"
    )

    lead_preservation = next(
        demand
        for demand in lead_from_the_front.demands
        if demand.dimension
        is StrategicDemand.KEY_MODEL_PRESERVATION
    )

    assert lead_preservation.capability == pytest.approx(
        0.5241126543209876,
    )