"""DEV-078-PITS-B2: production Surprise Attack contract tests.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace

import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from pits_surprise_attack_service import (
    PitsPriorityPhaseRequest, build_pits_surprise_attack_evidence,
)

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


def declared(**kwargs):
    return PitsPriorityPhaseRequest(
        azog_alive=kwargs.pop("azog_alive", True),
        azog_on_battlefield=kwargs.pop("azog_on_battlefield", True),
        already_used=kwargs.pop("already_used", False),
        declare_surprise_attack=kwargs.pop("declare_surprise_attack", True),
        **kwargs,
    )


def analyse(pits, request=None):
    army, army_list = pits
    options = {} if request is None else {"pits_surprise_attack_request": request}
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **options
    )


def test_real_import_registers_pits_rule_and_azog(pits):
    army, army_list = pits
    assert army_list.id == "DG_PITS"
    assert any(r.id == "DG_SURPRISE_ATTACK" for r in army_list.army_rules)
    assert any(m.configured_profile is not None and "azog" in m.configured_profile.profile.name.lower() for m in army.fielded_models())


def test_production_declared_priority_and_heroic_move_lock(pits):
    result = analyse(pits, declared())
    r = result["mechanical_pits_surprise_attack"]
    assert r.declared and r.used_after_phase and r.priority_winner == "pits"
    assert r.pits_must_take_priority and r.opposing_heroic_moves_prohibited


def test_absent_request_keeps_result_shape(pits):
    assert "mechanical_pits_surprise_attack" not in analyse(pits)


def test_declined_activation_has_no_effect(pits):
    r = analyse(pits, declared(declare_surprise_attack=False))["mechanical_pits_surprise_attack"]
    assert not r.declared and r.priority_winner is None


def test_simultaneous_pending_requires_real_result(pits):
    r = analyse(pits, declared(opponent_declares_equivalent_priority_rule=True))[
        "mechanical_pits_surprise_attack"]
    assert r.simultaneous_resolution_required and r.used_after_phase
    assert r.priority_winner is None


def test_simultaneous_opponent_win_consumes_rule(pits):
    r = analyse(pits, declared(
        opponent_declares_equivalent_priority_rule=True,
        simultaneous_roll_off_winner="opponent",
    ))["mechanical_pits_surprise_attack"]
    assert r.priority_winner == "opponent" and r.used_after_phase


def test_dead_azog_cannot_activate(pits):
    with pytest.raises(ValueError, match="alive"):
        analyse(pits, declared(azog_alive=False))


def test_inactive_army_rule_rejected(pits):
    army, army_list = pits
    inactive = SimpleNamespace(id="DG_PITS", army_rules=[])
    with pytest.raises(ValueError, match="active Surprise Attack"):
        build_pits_surprise_attack_evidence(army, inactive, request=declared())


def test_wrong_army_rejected(pits):
    army, army_list = pits
    other = SimpleNamespace(id="DG_ROTN", army_rules=army_list.army_rules)
    with pytest.raises(ValueError, match="Pits of Dol Guldur"):
        build_pits_surprise_attack_evidence(army, other, request=declared())


def test_existing_scores_unchanged(pits):
    before = analyse(pits)
    after = analyse(pits, declared())
    assert before["metric_assessments"] == after["metric_assessments"]
    assert before["battlefield_assessments"] == after["battlefield_assessments"]
    assert before["metric_densities"] == after["metric_densities"]


def test_no_dashboard_or_scenario_score(pits):
    r = analyse(pits, declared())["mechanical_pits_surprise_attack"]
    assert r.dashboard_score is None and r.scenario_score is None
