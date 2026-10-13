"""F4-A2 real production fixtures, conservation and no scoring leakage."""
from dataclasses import replace

import pytest

from army import Army
from mechanical_magic_fixture_validation import (
    compare_magic_fixtures, validate_magic_contract,
)
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_rise_of_the_necromancer_json_import_integration import (
    FIXTURE_PATH as RISE_FIXTURE, load_production_rise_data,
)
from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)
from services import army_analysis_service as service
from rule_loader import load_spells, load_ability_tags, load_ability_prerequisites
from relationship_loader import (
    load_profile_spells, load_spell_tags, load_spell_prerequisites,
)


def _hydrate_spell_relationships(profiles_by_id):
    """Mirror main.py's spell-loading stage for the partial fixture loader."""
    spells = load_spells()
    load_profile_spells(profiles_by_id, spells)
    load_spell_tags(spells, load_ability_tags())
    load_spell_prerequisites(spells, load_ability_prerequisites())




@pytest.fixture(scope="module")
def real_armies():
    rise_profiles, rise_lists, rise_opts = load_production_rise_data()
    _hydrate_spell_relationships(rise_profiles)
    _, rise, rise_list = import_army_from_mesbg_list_builder(
        RISE_FIXTURE, rise_profiles, rise_lists,
        profile_options_by_external_id=rise_opts,
    )
    azog_profiles, azog_lists, azog_opts = load_production_azogs_hunters_data()
    _hydrate_spell_relationships(azog_profiles)
    _, azog, azog_list = import_army_from_mesbg_list_builder(
        "tests/fixtures/azogs_hunters_all_options.json", azog_profiles, azog_lists,
        profile_options_by_external_id=azog_opts,
    )
    return (rise, rise_list), (azog, azog_list)


def test_real_necromancer_has_known_nine_spell_repertoire(real_armies):
    (rise, _), _ = real_armies
    report = compare_magic_fixtures((("rise", rise),))
    magic = report.rows[0].contract
    assert "COMPEL" in magic.distinct_spell_ids
    assert "CHILL_SOUL" in magic.distinct_spell_ids
    assert "YOUR_STAFF_IS_BROKEN" in magic.distinct_spell_ids
    assert magic.caster_count >= 1
    assert magic.starting_caster_will > 0
    assert report.rows[0].validation_errors == ()


def test_necromancer_effect_categories_are_only_labels(real_armies):
    (rise, _), _ = real_armies
    row = compare_magic_fixtures((("rise", rise),)).rows[0]
    assert any(c.tag_id == "CONTROL" for c in row.contract.effect_categories)
    assert row.contract.dashboard_score is None
    assert row.contract.scenario_score is None
    assert not hasattr(row.contract, "combined_magic_score")


def test_two_real_armies_have_separate_validated_rows(real_armies):
    (rise, _), (azog, _) = real_armies
    report = compare_magic_fixtures((("rise", rise), ("azog", azog)))
    assert tuple(row.label for row in report.rows) == ("rise", "azog")
    assert all(row.validation_errors == () for row in report.rows)
    assert report.dashboard_score is None and report.scenario_score is None
    assert all(row.contract.army_points > 0 for row in report.rows)


def test_no_magic_empty_army_has_no_invented_probability():
    contract = compare_magic_fixtures((("empty", Army()),)).rows[0].contract
    assert contract.one_will_probability_weighted_mean is None
    assert contract.one_will_attempt_ceiling == 0


def test_probability_out_of_bounds_is_flagged(real_armies):
    (rise, _), _ = real_armies
    valid = compare_magic_fixtures((("rise", rise),)).rows[0].contract
    assert "invalid casting probability" in validate_magic_contract(
        replace(valid, one_will_probability_weighted_mean=1.5)
    )


def test_resource_mismatch_is_flagged(real_armies):
    (rise, _), _ = real_armies
    valid = compare_magic_fixtures((("rise", rise),)).rows[0].contract
    assert "starting Will ledger inconsistent" in validate_magic_contract(
        replace(valid, starting_caster_will=valid.starting_caster_will + 1)
    )


def test_scoring_field_contamination_is_flagged(real_armies):
    (rise, _), _ = real_armies
    valid = compare_magic_fixtures((("rise", rise),)).rows[0].contract
    assert any("score" in e for e in validate_magic_contract(replace(valid, dashboard_score=0.5)))


def test_duplicate_fixture_labels_rejected():
    with pytest.raises(ValueError, match="unique"):
        compare_magic_fixtures((("a", Army()), ("a", Army())))


def test_invalid_fixture_input_rejected():
    with pytest.raises(TypeError, match="Army"):
        compare_magic_fixtures((("bad", object()),))


def test_non_tuple_fixture_input_rejected():
    with pytest.raises(TypeError, match="tuple"):
        compare_magic_fixtures([])


def test_service_diagnostics_do_not_override_scoring(monkeypatch, real_armies):
    (rise, rise_list), _ = real_armies
    marker_metrics, marker_scenarios = object(), object()
    captured = []
    monkeypatch.setattr(service, "calculate_army_metric_densities", lambda *_: object())
    monkeypatch.setattr(service, "calculate_army_offensive_output_density", lambda *_: 0.2)
    monkeypatch.setattr(service, "calculate_army_shooting_output_density", lambda **_: 0.4)
    monkeypatch.setattr(service, "normalise_shooting_output_density", lambda _: 0.5)
    monkeypatch.setattr(service, "calculate_mechanical_defence_diagnostics", lambda _: None)
    monkeypatch.setattr(service, "build_mobility_integration_contract", lambda _: None)
    monkeypatch.setattr(service, "build_courage_integration_contract", lambda *_: None)
    def assess(densities, thresholds, **kw):
        captured.append(kw)
        return marker_metrics
    monkeypatch.setattr(service, "assess_army_metrics", assess)
    monkeypatch.setattr(service, "assess_battlefield", lambda _ : marker_scenarios)
    result = service.analyse_imported_army(rise, rise_list, max(2000, rise.total_points()), object())
    assert result["mechanical_magic"] is not None
    assert result["metric_assessments"] is marker_metrics
    assert result["battlefield_assessments"] is marker_scenarios
    assert captured == [{"offence_value": 0.2, "shooting_value": 0.5}]
