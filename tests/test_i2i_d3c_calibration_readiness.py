"""D3-C focuses on fail-closed, evidence-classified readiness."""
from pathlib import Path
import pytest
from i2i_d3c_calibration_readiness import assess, load_evidence, GATES

ROOT = Path(__file__).resolve().parents[1]


def test_no_evidence_fails_closed():
    r = assess({})
    assert r["status"] == "blocked_by_evidence_gate"
    assert r["release_readiness"] == "not_ready"


def test_seven_pending_approval_gates():
    r = assess({})
    assert len(r["gates"]) == 7
    assert all(g["formal_approval"] == "pending" for g in r["gates"])
    assert r["gate_counts"]["formally_approved"] == 0


def test_evidence_class_is_not_approval():
    r = assess({})
    assert all(g["formal_approval"] == "pending" for g in r["gates"])


def test_frozen_candidate_unapproved():
    r = assess({})
    assert r["approved_method"] is None
    assert r["numerical_anchors"] is None
    assert r["numerical_calibration_permitted"] is False


def test_no_production_mutation():
    r = assess({})
    assert r["production_scoring_modified"] is False
    assert r["composite_score_calculated"] is False


def test_all_expected_gates_have_actions():
    assert set(GATES) == {f"G{i}" for i in range(1, 8)}
    assert all(g["next_action"] for g in assess({})["gates"])


@pytest.fixture(scope="module")
def evidence():
    filenames = (
        "b8c_reference_qualification.json", "i2i_d2c_cross_metric_archetype_report.json",
        "i2i_d3a_candidate_scales.json", "i2i_d3b_fixed_reference_methodology.json",
    )
    missing = [filename for filename in filenames if not (ROOT / filename).is_file()]
    assert not missing, f"Missing calibration evidence in {ROOT}: {missing}"
    return load_evidence(ROOT)


def test_existing_evidence_valid(evidence):
    r = assess(evidence)
    assert r["status"] == "readiness_audit_complete", r["source_gate_errors"]
    assert r["source_gate_errors"] == []


def test_evidence_classes_are_complete(evidence):
    r = assess(evidence)
    assert r["gate_counts"]["evidence_validated"] == 1
    assert r["gate_counts"]["evidence_conditional"] == 2
    assert r["gate_counts"]["evidence_outstanding"] == 4


def test_readiness_stays_blocked_on_good_evidence(evidence):
    r = assess(evidence)
    assert r["release_readiness"] == "not_ready"
    assert r["numerical_calibration_permitted"] is False
    assert r["gate_counts"]["pending"] == 7


def test_reject_unexpected_anchor_approval(evidence):
    import copy
    tampered = copy.deepcopy(evidence)
    tampered["d3b"]["calibration_anchors_approved"] = True
    assert assess(tampered)["status"] == "blocked_by_evidence_gate"


def test_reject_independent_defence_weighting(evidence):
    import copy
    tampered = copy.deepcopy(evidence)
    tampered["d3b"]["dependency_policy"]["independent_weighting_allowed"] = True
    assert assess(tampered)["status"] == "blocked_by_evidence_gate"


def test_reject_missing_approval_gate(evidence):
    import copy
    tampered = copy.deepcopy(evidence)
    tampered["d3b"]["approval_gates"].pop()
    assert assess(tampered)["status"] == "blocked_by_evidence_gate"
