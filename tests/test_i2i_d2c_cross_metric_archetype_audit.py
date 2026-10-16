"""Focused D2-C evidence-contract and descriptive-metric tests."""
import copy
from pathlib import Path

import pytest

from i2i_d2c_cross_metric_archetype_audit import (
    FILES, METRICS, ROOT, build_report, pearson, read_json,
)


@pytest.fixture(scope="module")
def data():
    missing = [name for name in FILES.values() if not (ROOT / name).is_file()]
    if missing:
        pytest.skip(f"Missing D2-C evidence files: {missing}")
    return {key: read_json(ROOT / name) for key, name in FILES.items()}


@pytest.fixture(scope="module")
def report(data):
    return build_report(data)


def test_pearson_handles_perfect_overlap_and_inverse():
    assert pearson([1, 2, 3], [2, 4, 6]) == pytest.approx(1)
    assert pearson([1, 2, 3], [6, 4, 2]) == pytest.approx(-1)


def test_pearson_rejects_constant_series():
    assert pearson([1, 1, 1], [1, 2, 3]) is None


def test_pearson_rejects_unequal_samples():
    assert pearson([1, 2], [1]) is None


def test_six_metric_dimensions_only():
    assert len(METRICS) == 6
    assert "magic" not in METRICS


def test_complete_matrix_and_15_pairs(report):
    assert report["status"] == "cross_metric_audit_complete", report.get("errors")
    assert report["armies"] == 6
    assert len(report["pairwise_correlations"]) == 15
    assert all(len(rank) == 6 for rank in report["rankings"].values())


def test_six_archetype_hypotheses_are_not_approvals(report):
    assert len(report["archetype_hypotheses"]) == 6
    assert all(h["approved"] is False for h in report["archetype_hypotheses"])


def test_defence_double_counting_risk_explicit(report):
    assert report["derived_metric_dependency"]["double_counting_warning"] is True


def test_woodland_and_chariot_caveats(report):
    joined = " ".join(report["exclusions"])
    assert "Woodland Creature" in joined
    assert "Chariot" in joined


def test_no_automatic_approval(report):
    assert report["numerical_calibration_permitted"] is False
    assert report["calibration_anchors_approved"] is False
    assert report["production_scoring_modified"] is False


def test_gate_rejects_invalid_qualification(data):
    mutated = dict(data)
    mutated["qualification"] = dict(data["qualification"], status="blocked")
    assert build_report(mutated)["status"] == "blocked_evidence"


def test_cross_source_disagreement_blocks(data):
    mutated = dict(data)
    changed = copy.deepcopy(data["movement_shooting"])
    changed["rows"][0]["measurements"]["mobility"]["open_ground"] += 1
    mutated["movement_shooting"] = changed
    report = build_report(mutated)
    assert report["status"] == "blocked_evidence"
    assert any("mobility_baseline_mismatch" in e for e in report["errors"])
