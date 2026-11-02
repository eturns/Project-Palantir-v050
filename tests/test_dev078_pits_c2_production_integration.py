"""DEV-078-PITS-C2 Stage 2 real-army integration acceptance.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
from types import SimpleNamespace
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from pits_thrain_imprisonment_service import (
    PitsThrainTestRequest, build_pits_thrain_imprisonment_evidence,
)
from shattered_spirit_state import ShatteredSpiritResult as Result

FIXTURE = Path(__file__).parent / "fixtures/pits_of_dol_guldur_all_options.json"

@pytest.fixture(scope="module")
def pits():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list

def req(**kwargs):
    params = dict(first_die=1, second_die=2, intelligence="6+",
                  keeper_on_battlefield=True, keeper_distance_inches=6.0)
    params.update(kwargs)
    return PitsThrainTestRequest(**params)

def analyse(pits, request=None):
    army, army_list = pits
    opts = {} if request is None else {"pits_thrain_test_request": request}
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **opts
    )

def test_registered_in_real_army(pits):
    army, army_list = pits
    assert army_list.id == "DG_PITS"
    assert sum(rule.id == "DG_THRAINS_IMPRISONMENT" for rule in army_list.army_rules) == 1
    names = [m.configured_profile.profile.name for m in army.fielded_models()
             if m.configured_profile is not None]
    assert sum(n in ("Thráin the Broken", "Thrain the Broken") for n in names) == 1
    assert names.count("The Keeper of the Dungeons") == 1

def test_real_army_failed_test_converted(pits):
    result = analyse(pits, req())
    ev = result["mechanical_pits_thrain_imprisonment"]
    assert ev.imprisonment_applied and ev.thrain_counts_as_evil
    assert ev.original_state.result is Result.OPPONENT_CONTROLLED
    assert ev.effective_state.result is Result.NORMAL

def test_failed_doubles_not_empowered(pits):
    ev = analyse(pits, req(first_die=2, second_die=2))["mechanical_pits_thrain_imprisonment"]
    assert ev.effective_state.result is Result.NORMAL

def test_successful_doubles_still_empowered(pits):
    ev = analyse(pits, req(first_die=4, second_die=4))["mechanical_pits_thrain_imprisonment"]
    assert ev.effective_state.result is Result.EMPOWERED

def test_beyond_six_does_not_override(pits):
    ev = analyse(pits, req(keeper_distance_inches=6.01))["mechanical_pits_thrain_imprisonment"]
    assert ev.effective_state.result is Result.OPPONENT_CONTROLLED

def test_absent_keeper_does_not_override(pits):
    ev = analyse(pits, req(keeper_on_battlefield=False, keeper_distance_inches=None))["mechanical_pits_thrain_imprisonment"]
    assert ev.effective_state.result is Result.OPPONENT_CONTROLLED

def test_rule_omitted_is_not_silently_granted(pits):
    army, army_list = pits
    inactive = SimpleNamespace(id="DG_PITS", army_rules=[
        r for r in army_list.army_rules if r.id != "DG_THRAINS_IMPRISONMENT"
    ])
    with pytest.raises(ValueError, match="active"):
        build_pits_thrain_imprisonment_evidence(army, inactive, request=req())

def test_no_request_has_no_derived_event(pits):
    assert "mechanical_pits_thrain_imprisonment" not in analyse(pits)

def test_original_scores_unchanged(pits):
    before, after = analyse(pits), analyse(pits, req())
    for name in ("metric_assessments", "battlefield_assessments", "metric_densities"):
        assert before[name] == after[name]

def test_uncalibrated_event(pits):
    ev = analyse(pits, req())["mechanical_pits_thrain_imprisonment"]
    assert ev.dashboard_score is None and ev.scenario_score is None
