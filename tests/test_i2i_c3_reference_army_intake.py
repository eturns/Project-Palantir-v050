"""DEV-077S-I2-I-C3-D6 intake tests; no fake roster is marked as real."""
import hashlib
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i2i_c3_reference_army_intake import (
    validate_intake_declaration, assess_intake_evidence, intake_roster,
)


def evidence(points=700, **overrides):
    obj = dict(source="fresh_real_army_engine_run", army_key="sample_army",
               points=points, models=12, roster_sha256="a" * 64,
               analysis_commit="a1b2c3", measurements=[{} for _ in range(10)],
               production_scoring_enabled=False, reference_anchors_approved=False,
               scenario_scoring_changed=False)
    obj.update(overrides)
    return obj


def assess(data=None, **kw):
    return assess_intake_evidence(data or evidence(), army_key="sample_army",
                                  alignment="Good", archetype="shooting", **kw)


@pytest.mark.parametrize("key", ["Abc", "x", "abc-d", "_abc", "x" * 65])
def test_invalid_keys(key):
    with pytest.raises(ValueError, match="army_key"):
        validate_intake_declaration(key, "Good", "shooting")


@pytest.mark.parametrize("alignment", ["Neutral", "good", "", None])
def test_invalid_alignment(alignment):
    with pytest.raises(ValueError, match="alignment"):
        validate_intake_declaration("sample_army", alignment, "shooting")


@pytest.mark.parametrize("archetype", ["unknown", "Shooter", "", None])
def test_invalid_archetype(archetype):
    with pytest.raises(ValueError, match="archetype"):
        validate_intake_declaration("sample_army", "Good", archetype)


def test_valid_declaration():
    validate_intake_declaration("sample_army", "Good", "shooting")


def test_qualified_does_not_approve_scoring_or_alignment():
    v = assess()
    assert v["points_and_evidence_qualified"]
    assert not v["calibration_eligible"]
    assert not v["alignment_and_archetype_verified"]
    assert not v["anchors_approved"]


@pytest.mark.parametrize("change,blocker", [
    ({"points": 694}, "outside_reference_points_range"),
    ({"models": 0}, "no_fielded_models"),
    ({"roster_sha256": "oops"}, "missing_valid_roster_hash"),
    ({"analysis_commit": ""}, "missing_engine_commit"),
    ({"measurements": []}, "missing_ten_metric_evidence"),
    ({"production_scoring_enabled": True}, "unexpected_scoring_activation"),
    ({"source": "historical_scenario"}, "not_fresh_engine_evidence"),
    ({"army_key": "other"}, "army_key_mismatch"),
])
def test_blockers(change, blocker):
    assert blocker in assess(evidence(**change))["blockers"]


def test_hash_mismatch():
    assert "roster_hash_mismatch" in assess(expected_sha256="b" * 64)["blockers"]


def test_refuses_existing_output(tmp_path):
    roster = tmp_path / "army.json"
    roster.write_text("{}")
    with pytest.raises(ValueError, match="overwrite"):
        intake_roster(fixture=roster, output=roster, army_key="sample_army",
                      alignment="Good", archetype="shooting")


def test_rejected_roster_not_written(tmp_path):
    roster = tmp_path / "army.json"
    roster.write_text("{}")
    output = tmp_path / "output.json"
    fake = evidence(points=694, roster_sha256=hashlib.sha256(roster.read_bytes()).hexdigest())
    with patch("i2i_c3_reference_army_intake.run_evidence", return_value=fake):
        result = intake_roster(fixture=roster, output=output, army_key="sample_army",
                               alignment="Good", archetype="shooting")
    assert "outside_reference_points_range" in result["blockers"]
    assert not output.exists()


def test_accepted_roster_retains_review_blockers(tmp_path):
    roster = tmp_path / "army.json"
    roster.write_text("{}")
    output = tmp_path / "output.json"
    fake = evidence(roster_sha256=hashlib.sha256(roster.read_bytes()).hexdigest())
    with patch("i2i_c3_reference_army_intake.run_evidence", return_value=fake):
        result = intake_roster(fixture=roster, output=output, army_key="sample_army",
                               alignment="Good", archetype="shooting")
    assert result["points_and_evidence_qualified"]
    assert not result["calibration_eligible"]
    assert output.exists()


@pytest.mark.parametrize("points,accepted", [(694, False), (695, True), (697, True), (700, True), (701, False)])
def test_d7_reference_points_boundaries(points, accepted):
    verdict = assess(evidence(points=points))
    assert verdict["points_and_evidence_qualified"] is accepted
    assert verdict["min_reference_points"] == 695
    assert verdict["max_reference_points"] == 700
    assert not verdict["anchors_approved"]


def test_bool_points_not_accepted():
    assert "outside_reference_points_range" in assess(evidence(points=True))["blockers"]


def test_qualified_697_is_persisted_but_not_calibration_approved(tmp_path):
    roster = tmp_path / "army.json"
    roster.write_text("{}")
    output = tmp_path / "evidence.json"
    fake = evidence(points=697, roster_sha256=hashlib.sha256(roster.read_bytes()).hexdigest())
    with patch("i2i_c3_reference_army_intake.run_evidence", return_value=fake):
        verdict = intake_roster(fixture=roster, output=output, army_key="sample_army",
                                alignment="Evil", archetype="cavalry")
    assert verdict["points_and_evidence_qualified"]
    assert not verdict["calibration_eligible"]
    assert output.exists()
