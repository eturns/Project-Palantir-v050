"""Regression checks for I2-I-D2-B1 read-only sensitivity."""
from dataclasses import replace

import pytest

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from i2i_d2b1_combat_benchmark_sensitivity import (
    BENCHMARKS, METRICS, build_report, gate_ok, rankings,
)

def test_fixed_baseline_is_unchanged():
    assert BENCHMARKS["baseline_f4_s4_d6"] == DEFAULT_COMBAT_BENCHMARK

def test_one_dimension_varies_at_a_time():
    baseline = BENCHMARKS["baseline_f4_s4_d6"]
    names = ("fight", "strength", "defence", "attacks", "wounds")
    for key, benchmark in BENCHMARKS.items():
        if key == "baseline_f4_s4_d6":
            continue
        assert sum(getattr(benchmark, n) != getattr(baseline, n)
                   for n in names) == 1

def test_benchmarks_include_opponent_defence_strength_and_fight():
    assert {"defender_d4", "defender_d8", "opponent_s3",
            "opponent_s6", "opponent_f5"} <= set(BENCHMARKS)

def test_only_combat_measures():
    assert METRICS == ("offence_density", "army_survival_density",
                       "per_model_resilience")

def test_denied_qualification_blocks_before_import():
    def cannot_import(_):
        raise AssertionError("must not import on unapproved evidence")
    report = build_report({"stage":"B8-C","status":"blocked"}, cannot_import)
    assert report["status"] == "blocked_by_qualification_gate"

def test_gate_rejects_anchor_approval():
    assert not gate_ok({"stage":"B8-C","status":"provisional_evidence_qualified",
                        "calibration_anchors_approved":True})

def test_rankings_deterministic_for_ties():
    rows = [
        {"army":"z","measurements":{"offence_density":0.3}},
        {"army":"a","measurements":{"offence_density":0.3}},
    ]
    assert rankings(rows, "offence_density") == ["a", "z"]

@pytest.fixture(scope="module")
def report():
    from pathlib import Path
    from i2i_c3_b8c_reference_qualification import read_json
    p = Path(__file__).resolve().parents[1] / "b8c_reference_qualification.json"
    if not p.is_file():
        pytest.skip("B8-C evidence not present in project root")
    return build_report(read_json(p))

def test_six_armies_per_benchmark(report):
    assert len(report["benchmark_results"]) == len(BENCHMARKS)
    for case in report["benchmark_results"]:
        assert len(case["rows"]) == 6

def test_results_are_finite_and_unapproved(report):
    import math
    assert report["status"] == "benchmark_sensitivity_complete", report
    for case in report["benchmark_results"]:
        for row in case["rows"]:
            assert set(row["measurements"]) == set(METRICS)
            assert all(math.isfinite(v) for v in row["measurements"].values())
    assert report["numerical_calibration_permitted"] is False
    assert report["production_scoring_modified"] is False

def test_baseline_recovers_existing_d1_values(report):
    from i2i_c3_b8c_reference_qualification import read_json
    import json
    from pathlib import Path
    p=Path(__file__).resolve().parents[1]/"i2i_d1_measurement_matrix.json"
    if not p.exists():
        pytest.skip("D1 measurement evidence not present")
    baseline = report["benchmark_results"][0]["rows"]
    original = {r["army"]:r for r in read_json(p)["rows"]}
    for row in baseline:
        assert row["measurements"]["offence_density"] == pytest.approx(
            original[row["army"]]["measurements"]["offence"]["value"])
        assert row["measurements"]["army_survival_density"] == pytest.approx(
            original[row["army"]]["measurements"]["defence"]["value"])
