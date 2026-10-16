"""Focused tests for D3-B governance design and fail-closed behaviour."""
from pathlib import Path

import pytest
from i2i_d3b_fixed_reference_methodology import (
    build_report, load_sources, source_gate, approval_gates, method_specifications,
    read_json,
)

ROOT = Path(__file__).resolve().parents[1]


def test_invalid_sources_fail_closed():
    r = build_report({})
    assert r["status"] == "blocked_by_evidence_gate"
    assert r["numerical_calibration_permitted"] is False

def test_no_anchor_value_or_production_score():
    r = build_report({})
    assert r["candidate_anchor_values"] is None
    assert r["approved_method"] is None
    assert r["composite_score_calculated"] is False
    assert r["production_scoring_modified"] is False

def test_references_are_not_recalibrated_when_lists_change():
    spec = method_specifications()
    assert any("Never refit" in s for s in spec["reference_policy"])

def test_versions_require_new_approval():
    spec = method_specifications()
    assert "independent approval" in spec["versioning"]["revision_requires"]

def test_defence_not_independently_weighted():
    r = build_report({})
    assert r["dependency_policy"]["independent_weighting_allowed"] is False

def test_every_approval_gate_pending():
    gates = approval_gates()
    assert len(gates) == 7
    assert all(g["state"] == "pending" for g in gates)

def test_gate_does_not_trust_mislabelled_sources():
    assert source_gate({"d3a": {"stage": "I2-I-D3-A",
                               "status": "illustrative_scales_complete",
                               "calibration_anchors_approved": True}})

@pytest.fixture(scope="module")
def source_report():
    if any(not (ROOT / x).exists() for x in (
        "b8c_reference_qualification.json", "i2i_d2c_cross_metric_archetype_report.json",
        "i2i_d3a_candidate_scales.json",
    )):
        pytest.skip("Expected source reports not found in project root")
    return build_report(load_sources(ROOT))

def test_evidence_gate_accepts_known_cohort(source_report):
    assert source_report["status"] == "methodology_documented", source_report["source_gate_errors"]

def test_report_carries_known_exclusions(source_report):
    assert any("Woodland Creature" in x for x in source_report["unresolved_exclusions"])
    assert any("Chariot" in x for x in source_report["unresolved_exclusions"])

def test_no_production_permission_even_with_valid_sources(source_report):
    assert source_report["numerical_calibration_permitted"] is False
    assert source_report["calibration_anchors_approved"] is False

def test_utf16_json_accepted(tmp_path):
    p = tmp_path / "report.json"
    p.write_text('{"stage":"test"}', encoding="utf-16")
    assert read_json(p)["stage"] == "test"
