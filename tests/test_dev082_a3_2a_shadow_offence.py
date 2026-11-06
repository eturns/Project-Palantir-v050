"""DEV-082-A3-2A — opt-in shadow evidence regression contract."""
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest
import offence_shadow_evidence as shadow


def _army(*quantities):
    entries = [SimpleNamespace(
        counts_as_model=True, quantity=qty,
        configured_profile=SimpleNamespace(profile=SimpleNamespace(id=f'MODEL_{i}')),
    ) for i, qty in enumerate(quantities)]
    return SimpleNamespace(entries=entries, total_points=lambda: 700)


def _contract(**overrides):
    values = dict(heroic=None, weighted_baseline=None,
                  uncharged=0.2, charged=0.3, eligible_cavalry_charge=0.4,
                  unresolved_context=('charge_probability_unknown',),
                  evidence_status='baseline_only_not_calibrated')
    values.update(overrides)
    return SimpleNamespace(**values)


def _patch(monkeypatch, legacy=0.693, contract=None):
    calls = {'legacy': 0, 'contract': 0}
    def old(*args):
        calls['legacy'] += 1
        return legacy
    def new(*args):
        calls['contract'] += 1
        return contract if contract is not None else _contract()
    monkeypatch.setattr(shadow, 'calculate_army_offensive_output_density', old)
    monkeypatch.setattr(shadow, 'calculate_mechanical_offence_contract', new)
    return calls


def test_disabled_is_default_and_does_not_execute_calculators(monkeypatch):
    calls = _patch(monkeypatch)
    value = shadow.collect_shadow_offence_evidence(_army(4))
    assert not value.enabled and value.legacy_raw_density is None
    assert value.profiles == () and calls == {'legacy': 0, 'contract': 0}


def test_opt_in_collects_legacy_and_separate_model_evidence(monkeypatch):
    calls = _patch(monkeypatch)
    value = shadow.collect_shadow_offence_evidence(_army(4, 2), enabled=True)
    assert value.legacy_raw_density == 0.693
    assert [(p.profile_id, p.quantity) for p in value.profiles] == [('MODEL_0', 4), ('MODEL_1', 2)]
    assert calls == {'legacy': 1, 'contract': 2}


def test_never_invents_comparable_candidate_or_display_score(monkeypatch):
    _patch(monkeypatch)
    value = shadow.collect_shadow_offence_evidence(_army(1), enabled=True)
    assert value.candidate_raw_density is None and value.dashboard_score is None
    assert value.scenario_score is None and value.comparable is False
    assert value.evidence_status == 'conditional_not_comparable'


def test_explicit_context_unknown_and_weighted_value_not_inferred(monkeypatch):
    _patch(monkeypatch)
    value = shadow.collect_shadow_offence_evidence(_army(1), enabled=True)
    assert value.profiles[0].weighted_probability is None
    assert 'charge_probability_unknown' in value.profiles[0].unresolved_context


def test_zero_model_army_is_not_fabricated_output(monkeypatch):
    calls = _patch(monkeypatch, legacy=0)
    value = shadow.collect_shadow_offence_evidence(_army(), enabled=True)
    assert value.legacy_raw_density == 0 and not value.profiles
    assert calls == {'legacy': 1, 'contract': 0}

@pytest.mark.parametrize('bad', [-0.1, float('nan'), float('inf')])
def test_bad_legacy_readings_fail_closed(monkeypatch, bad):
    _patch(monkeypatch, legacy=bad)
    with pytest.raises(ValueError):
        shadow.collect_shadow_offence_evidence(_army(1), enabled=True)

@pytest.mark.parametrize('bad', [-0.1, float('nan'), 1.01])
def test_bad_new_probabilities_fail_closed(monkeypatch, bad):
    _patch(monkeypatch, contract=_contract(uncharged=bad))
    with pytest.raises(ValueError):
        shadow.collect_shadow_offence_evidence(_army(1), enabled=True)


def test_unqualified_weighted_output_rejected(monkeypatch):
    _patch(monkeypatch, contract=_contract(weighted_baseline=0.25))
    with pytest.raises(ValueError, match='unqualified shadow'):
        shadow.collect_shadow_offence_evidence(_army(1), enabled=True)


def test_unexpected_heroic_allocation_rejected(monkeypatch):
    _patch(monkeypatch, contract=_contract(heroic=object()))
    with pytest.raises(ValueError, match='unqualified shadow'):
        shadow.collect_shadow_offence_evidence(_army(1), enabled=True)


def test_unsupported_mechanics_propagate_not_zero(monkeypatch):
    _patch(monkeypatch)
    def unsupported(*args):
        raise ValueError('unsupported context')
    monkeypatch.setattr(shadow, 'calculate_mechanical_offence_contract', unsupported)
    with pytest.raises(ValueError, match='unsupported context'):
        shadow.collect_shadow_offence_evidence(_army(1), enabled=True)


def test_opt_in_requires_real_army_evidence():
    with pytest.raises(TypeError):
        shadow.collect_shadow_offence_evidence(None, enabled=True)


def test_opt_in_requires_explicit_boolean():
    with pytest.raises(TypeError):
        shadow.collect_shadow_offence_evidence(_army(1), enabled=1)


def test_frozen_output_prevents_in_place_relabelling(monkeypatch):
    _patch(monkeypatch)
    result = shadow.collect_shadow_offence_evidence(_army(1), enabled=True)
    with pytest.raises(FrozenInstanceError):
        result.comparable = True
