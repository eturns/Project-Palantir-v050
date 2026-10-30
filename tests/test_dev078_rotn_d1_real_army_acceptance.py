"""DEV-078-ROTN-D1: real List Builder army / opt-in resistance acceptance.

Author: Edward Turns (Project Lead)
Read-only acceptance. No scoring, calibration or dashboard modifications.
"""
from pathlib import Path

import pytest

from army_loader import load_army_rules
from rotn_army_magic_service_adapter import (
    build_army_magic_resistance_inventory,
    analyse_imported_army_with_magic_resistance,
)
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)
from analysis_loader import load_metric_thresholds

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "rise_of_the_necromancer_all_options.json"


@pytest.fixture(scope="module")
def imported():
    assert FIXTURE.is_file(), f"Required existing fixture not found: {FIXTURE}"
    profiles, lists, options = load_production_azogs_hunters_data()
    # The shared production test helper registers lists but does not attach army rules.
    # Explicitly load the existing registry without altering its CSV.
    load_army_rules(lists)
    definition, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE),
        profiles_by_id=profiles,
        army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return definition, army, army_list


def test_real_fixture_is_rise(imported):
    definition, army, army_list = imported
    assert definition.army_list_id == army_list.id == "DG_ROTN"
    assert army.model_count() > 0
    assert any(m.profile_id == "DG_NEC" for m in army.fielded_models())


def test_existing_canonical_army_rules_loaded(imported):
    _, _, army_list = imported
    assert {rule.id for rule in army_list.army_rules} == {
        "DG_POWER_OF_THE_NECROMANCER", "DG_HIS_SPIRIT"
    }


def test_every_real_fielded_model_receives_army_resistance(imported):
    _, army, army_list = imported
    inventory = build_army_magic_resistance_inventory(army, army_list)
    actual_ids = tuple(model.id for model in army.fielded_models())
    assert inventory.eligible_model_ids == actual_ids
    assert inventory.model_count == len(actual_ids)
    assert inventory.source_rule_id == "DG_POWER_OF_THE_NECROMANCER"
    assert inventory.dashboard_score is inventory.scenario_score is None


def test_opt_in_service_preserves_existing_metric_objects(imported):
    _, army, army_list = imported
    thresholds = load_metric_thresholds()
    # Invoke both paths against identical real imported army.  This checks the
    # opt-in output path, NOT the normal List Builder service's default wiring.
    from services.army_analysis_service import analyse_imported_army
    standard = analyse_imported_army(army, army_list, army.total_points(), thresholds)
    enhanced = analyse_imported_army_with_magic_resistance(
        army, army_list, army.total_points(), thresholds
    )
    assert "mechanical_army_magic_resistance" in standard
    assert standard["mechanical_army_magic_resistance"] == enhanced["mechanical_army_magic_resistance"]
    assert enhanced["mechanical_army_magic_resistance"].eligible_model_ids
    assert enhanced["metric_assessments"] == standard["metric_assessments"]
    assert enhanced["battlefield_assessments"] == standard["battlefield_assessments"]
