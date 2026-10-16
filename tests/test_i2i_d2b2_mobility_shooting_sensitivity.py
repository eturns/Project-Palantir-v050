"""Focused read-only terrain and ranged shooting sensitivity checks."""
from pathlib import Path
import math

import pytest

from i2i_d2b2_mobility_shooting_sensitivity import (
    build_report, gate_ok, shoot_density, descending_rank,
)
from i2i_c3_b8c_reference_qualification import read_json

ROOT = Path(__file__).resolve().parents[1]

def test_invalid_reference_gate_denied_before_import():
    def denied(_):
        raise AssertionError("Importer must not run")
    report = build_report({"stage": "B8-C", "status": "blocked"}, importer=denied)
    assert report["status"] == "blocked_by_qualification_gate"

def test_gate_does_not_accept_anchor_approval():
    assert not gate_ok({"stage":"B8-C","status":"provisional_evidence_qualified",
                        "calibration_anchors_approved":True})

def test_rank_order_stable_for_ties():
    rows = [
        {"army":"z", "measurements":{"shooting":{"stationary":1.0}}},
        {"army":"a", "measurements":{"shooting":{"stationary":1.0}}},
    ]
    assert descending_rank(rows, "shooting", "stationary") == ["a", "z"]

@pytest.fixture(scope="module")
def report():
    p=ROOT/"b8c_reference_qualification.json"
    if not p.exists():
        pytest.skip("B8-C qualification evidence unavailable")
    return build_report(read_json(p))

def test_all_six_armies_import(report):
    assert report["status"] == "sensitivity_complete", report["errors"]
    assert len(report["rows"]) == 6

def test_mobility_retention_is_consistent(report):
    for row in report["rows"]:
        m=row["measurements"]["mobility"]
        assert m["open_ground"] >= 0
        assert m["difficult_terrain"] >= 0
        assert m["terrain_retention"] == pytest.approx(
            m["difficult_terrain"] / m["open_ground"]
            if m["open_ground"] else 0
        )

def test_moving_shooting_never_better_under_same_conditions(report):
    for row in report["rows"]:
        s=row["measurements"]["shooting"]
        assert s["moved_this_turn"] <= s["stationary"] + 1e-10
        assert all(math.isfinite(s[key]) for key in ("stationary","moved_this_turn"))

def test_zero_shooters_is_real_zero_not_missing(report):
    dg=next(r for r in report["rows"] if r["army"]=="dol_guldur")
    m=dg["measurements"]
    assert m["ranged_model_count"] == 0
    assert m["shooting"]["stationary"] == 0
    assert m["shooting"]["retention_when_moving"] is None

def test_rangers_have_shooting_evidence(report):
    ranger=next(r for r in report["rows"] if r["army"]=="rangers_of_mirkwood")
    assert ranger["measurements"]["ranged_model_count"] > 0
    assert ranger["measurements"]["shooting"]["stationary"] > 0

def test_no_calibration_or_scoring_changes(report):
    assert report["production_scoring_modified"] is False
    assert report["numerical_calibration_permitted"] is False
    assert report["calibration_anchors_approved"] is False
