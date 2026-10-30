"""DEV-078-ROTN-D5 Stage 2: production acceptance for declared Resist Tests.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
import pytest

from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from rotn_army_resistance_outcomes_service import (
    ResistanceRequest, build_army_resistance_outcomes,
)

FIXTURE = Path(__file__).parent / "fixtures/rise_of_the_necromancer_all_options.json"


@pytest.fixture(scope="module")
def rise():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list


def analyse(rise, **requests):
    army, army_list = rise
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **requests,
    )


def model_id(rise):
    return rise[0].fielded_models()[0].id


def test_free_die_from_rise_rule(rise):
    request = ResistanceRequest(cast_highest=4, will_available=0)
    result = analyse(rise, rotn_resistance_requests_by_model_id={model_id(rise): request})
    evidence = result["mechanical_army_resistance_outcomes"]
    assert evidence.source_rule_id == "DG_POWER_OF_THE_NECROMANCER"
    assert evidence.outcomes_by_model_id[0][1].probability_resisted == pytest.approx(0.5)
    assert evidence.outcomes_by_model_id[0][1].free_dice == 1


def test_will_spent_and_free_die_do_not_double_count(rise):
    result = analyse(rise, rotn_resistance_requests_by_model_id={
        model_id(rise): ResistanceRequest(cast_highest=4, will_available=2, will_spent=1, hero=True)
    })
    r = result["mechanical_army_resistance_outcomes"].outcomes_by_model_id[0][1]
    assert r.dice_total == 2 and r.will_after_spend == 1
    assert r.expected_hero_will_refund == pytest.approx(1/6)


def test_unknown_model_rejected(rise):
    with pytest.raises(ValueError, match="not fielded"):
        analyse(rise, rotn_resistance_requests_by_model_id={
            "not-a-real-model": ResistanceRequest(cast_highest=4, will_available=0)
        })


def test_no_request_leaves_existing_shape_alone(rise):
    result = analyse(rise)
    assert "mechanical_army_magic_resistance" in result
    assert "mechanical_army_resistance_outcomes" not in result


def test_empty_request_explicit_evidence(rise):
    result = analyse(rise, rotn_resistance_requests_by_model_id={})
    assert result["mechanical_army_resistance_outcomes"].outcomes_by_model_id == ()


def test_scores_unchanged_by_declared_resistance(rise):
    before = analyse(rise)
    after = analyse(rise, rotn_resistance_requests_by_model_id={
        model_id(rise): ResistanceRequest(cast_highest=6, will_available=0)
    })
    assert before["metric_assessments"] == after["metric_assessments"]
    assert before["battlefield_assessments"] == after["battlefield_assessments"]
    assert before["mechanical_necromancer_cast_sequence"] == after["mechanical_necromancer_cast_sequence"]


def test_adapter_supports_pits_grant_with_no_duplicate_logic(monkeypatch, rise):
    from types import SimpleNamespace
    army, _ = rise
    pits = SimpleNamespace(id="DG_PITS", army_rules=[SimpleNamespace(id="DG_MAGICAL_VOID")])
    report = build_army_resistance_outcomes(
        army, pits,
        requests_by_model_id={model_id(rise): ResistanceRequest(cast_highest=4, will_available=0)},
    )
    assert report.source_rule_id == "DG_MAGICAL_VOID"
    assert report.outcomes_by_model_id[0][1].free_dice == 1


def test_inactive_rule_has_no_free_die(rise):
    from types import SimpleNamespace
    army, _ = rise
    inactive = SimpleNamespace(id="DG_PITS", army_rules=[])
    report = build_army_resistance_outcomes(
        army, inactive,
        requests_by_model_id={model_id(rise): ResistanceRequest(cast_highest=4, will_available=0)},
    )
    assert report.source_rule_id is None
    assert report.outcomes_by_model_id[0][1].probability_resisted == 0
