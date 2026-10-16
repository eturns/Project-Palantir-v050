"""I2-I-P2-B presentation contract regression tests."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from provisional_desktop_view import build_provisional_desktop_view, build_provisional_summary


def defence():
    return {
        'army_survival_density': {'value': 2.9270251837875314, 'calibrated': False},
        'per_model_resilience': {'value': 0.5246129752480729, 'calibrated': False},
    }


def rows(panel):
    return {r['metric_id']: r for r in panel['metrics']}


def test_defence_is_provisionally_calibrated_but_not_weighted():
    p = build_provisional_desktop_view(defence())
    data = rows(p)
    assert data['army_survival_density']['rating'] == pytest.approx(1)
    assert data['per_model_resilience']['rating'] is not None
    assert p['defence_independent_composite_weighting_allowed'] is False
    assert p['production_scoring_changed'] is False


def test_without_mechanics_everything_is_not_evaluated():
    data = rows(build_provisional_desktop_view(None))
    assert all(x['rating'] is None for x in data.values())
    assert all(x['status'] == 'not_evaluated' for x in data.values())


def test_legacy_values_are_not_implicitly_reused():
    p = build_provisional_desktop_view(defence())
    assert rows(p)['offence_density']['rating'] is None
    assert rows(p)['magic']['rating'] is None


def test_explicit_qualified_measurement_has_frozen_score():
    p = build_provisional_desktop_view(None, qualified_measurements={'offence_density': 0.6180555555555556}, evidence_statuses={'offence_density': 'evaluated'})
    assert rows(p)['offence_density']['rating'] == pytest.approx(0.49777833755014805)
    assert rows(p)['offence_density']['status'] == 'evaluated'
    assert rows(p)['offence_density']['raw_value'] == pytest.approx(0.6180555555555556)


def test_measurement_without_qualification_is_not_evaluated():
    p = build_provisional_desktop_view(None, qualified_measurements={'offence_density': 0.7})
    assert rows(p)['offence_density']['rating'] is None


def test_conditional_evidence_is_not_zero():
    p = build_provisional_desktop_view(None, qualified_measurements={'open_ground_mobility': 6}, evidence_statuses={'open_ground_mobility': 'conditional'})
    row = rows(p)['open_ground_mobility']
    assert row['status'] == 'conditional'
    assert row['rating'] is None
    assert 'Conditional' in build_provisional_summary(p)


def test_conflicting_defence_values_rejected():
    with pytest.raises(ValueError, match='Conflicting'):
        build_provisional_desktop_view(defence(), qualified_measurements={'per_model_resilience': 0.7})


def test_unapproved_defence_input_rejected():
    data = defence()
    data['per_model_resilience']['calibrated'] = True
    with pytest.raises(ValueError, match='uncalibrated'):
        build_provisional_desktop_view(data)


def test_preview_has_provisional_label_and_no_scoring_claim():
    s = build_provisional_summary(build_provisional_desktop_view(defence()))
    assert 'PROVISIONAL' in s
    assert 'scenario and optimiser results unchanged' in s


def test_adapter_preserves_scenario_data(monkeypatch):
    import types
    import importlib.util
    import sys
    main = types.ModuleType('main')
    main.run_analysis_workflow = lambda file_path, print_report=False: {'unchanged': True}
    vm = types.ModuleType('desktop_analysis_view_model')
    vm.build_desktop_analysis_view_model = lambda result: {'scenarios': ('original',), 'defence_presentation': None}
    monkeypatch.setitem(sys.modules, 'main', main)
    monkeypatch.setitem(sys.modules, 'desktop_analysis_view_model', vm)
    path = ROOT / 'src' / 'desktop_analysis_adapter.py'
    spec = importlib.util.spec_from_file_location('_p2b_test_adapter', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = module.run_analysis('fixture.json')
    assert output['scenarios'] == ('original',)
    assert output['provisional_capabilities']['display_only'] is True
