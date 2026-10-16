"""Provisional display wiring: qualified mechanics only, never legacy values."""
from types import SimpleNamespace
import pytest

from provisional_calibration import CONDITIONAL, EVALUATED, NOT_EVALUATED
import provisional_mechanical_measurements as m
import desktop_analysis_adapter as adapter


def test_null_army_never_promotes_missing_to_zero():
    result = m.collect_provisional_mechanical_evidence(None)
    assert result.values == {}
    assert set(result.statuses.values()) == {NOT_EVALUATED}


def test_measurement_accepts_genuine_zero():
    result = m.ProvisionalMechanicalEvidence()
    m._measurement(result, 'stationary_shooting', lambda: 0)
    assert result.values['stationary_shooting'] == 0
    assert result.statuses['stationary_shooting'] == EVALUATED


@pytest.mark.parametrize('bad', [float('nan'), float('inf'), -1])
def test_invalid_measurements_are_conditional_not_zero(bad):
    result = m.ProvisionalMechanicalEvidence()
    m._measurement(result, 'offence_density', lambda: bad)
    assert 'offence_density' not in result.values
    assert result.statuses['offence_density'] == CONDITIONAL


def test_missing_mechanical_context_remains_conditional():
    result = m.ProvisionalMechanicalEvidence()
    m._measurement(result, 'stationary_shooting', lambda: (_ for _ in ()).throw(ValueError('incomplete bow')))
    assert result.statuses['stationary_shooting'] == CONDITIONAL
    assert 'incomplete bow' in result.reasons['stationary_shooting']


def test_mechanical_evidence_is_not_a_score_or_composite():
    assert 'score' not in vars(m.ProvisionalMechanicalEvidence())
    assert len(m.METRICS) == 4
    assert 'army_survival_density' not in m.METRICS


def test_adapter_preserves_original_view_object(monkeypatch):
    original = {'army_name': 'Fake', 'scenarios': ({'score': 0.4},), 'metrics': ({'value': 0.7},)}
    monkeypatch.setattr(adapter, 'run_analysis_workflow', lambda *a, **k: {'army': object()})
    monkeypatch.setattr(adapter, 'build_desktop_analysis_view_model', lambda r: original)
    panel = {'metrics': ('test',)}
    monkeypatch.setattr(adapter, 'build_provisional_desktop_view', lambda *a, **k: panel)
    assert adapter.run_analysis('fake.json') is original
    assert original['scenarios'] == ({'score': 0.4},)
    assert original['metrics'] == ({'value': 0.7},)
    assert original['provisional_capabilities'] is panel


def test_adapter_sends_mechanical_evidence_only_for_army(monkeypatch):
    class FakeArmy:
        pass
    monkeypatch.setattr(adapter, 'Army', FakeArmy)
    army = FakeArmy()
    monkeypatch.setattr(adapter, 'run_analysis_workflow', lambda *a, **k: {'army': army})
    monkeypatch.setattr(adapter, 'build_desktop_analysis_view_model', lambda r: {'defence_presentation': None})
    mechanical = m.ProvisionalMechanicalEvidence(
        values={'offence_density': 0.5}, statuses={'offence_density': EVALUATED})
    monkeypatch.setattr(adapter, 'collect_provisional_mechanical_evidence', lambda a: mechanical)
    captured = {}
    def panel(defence, **kw):
        captured.update(kw)
        return {'display_only': True}
    monkeypatch.setattr(adapter, 'build_provisional_desktop_view', panel)
    output = adapter.run_analysis('army.json')
    assert captured['qualified_measurements'] == {'offence_density': 0.5}
    assert captured['evidence_statuses']['offence_density'] == EVALUATED
    assert output['provisional_capabilities']['display_only'] is True
