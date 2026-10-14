"""DEV-077S-I2-I-A4 read-only dependency audit tests."""
from dataclasses import replace
import pytest
import unified_capability_overlap_audit as audit
from unified_capability_inventory import METRIC_NAMES


def test_audit_validates():
    result = audit.validate_overlap_audit()
    assert result.source_commit == '51ad0f1'
    assert result.risk_count == 9
    assert result.scoring_changed is False


def test_all_ten_capabilities_represented():
    assert audit.validate_overlap_audit().capabilities_covered == METRIC_NAMES


@pytest.mark.parametrize('risk', audit.RISKS, ids=lambda r: r.identifier)
def test_each_risk_has_explicit_prevention(risk):
    assert len(risk.capabilities) >= 2
    assert risk.shared_evidence and risk.risk and risk.required_control
    assert risk.disposition == 'needs_calibration_contract'


@pytest.mark.parametrize('metric', METRIC_NAMES)
def test_filter_returns_only_relevant_risks(metric):
    results = audit.get_overlap_risks(metric)
    assert results
    assert all(metric in r.capabilities for r in results)


def test_full_query_is_identity():
    assert audit.get_overlap_risks() == audit.RISKS


def test_unknown_metric_is_not_silently_accepted():
    with pytest.raises(KeyError):
        audit.get_overlap_risks('not_a_metric')


def test_missing_resource_safeguards_not_accepted(monkeypatch):
    monkeypatch.setattr(audit, 'RISKS', (
        replace(audit.RISKS[0], required_control=''),
    ))
    with pytest.raises(ValueError, match='Missing evidence'):
        audit.validate_overlap_audit()


def test_duplicate_ids_rejected(monkeypatch):
    monkeypatch.setattr(audit, 'RISKS', (audit.RISKS[0], audit.RISKS[0]))
    with pytest.raises(ValueError, match='unique'):
        audit.validate_overlap_audit()


def test_unknown_capability_rejected(monkeypatch):
    monkeypatch.setattr(audit, 'RISKS', (
        replace(audit.RISKS[0], capabilities=('magic', 'not_real')),
    ))
    with pytest.raises(ValueError, match='Unknown capability'):
        audit.validate_overlap_audit()
