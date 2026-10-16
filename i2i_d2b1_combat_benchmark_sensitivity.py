"""DEV-077S-I2-I-D2-B1: read-only combat benchmark sensitivity.

Use the six provisionally qualified army fixtures. No inferred rules,
fitted weights, automatic approvals or production score modification.
"""
import json
from dataclasses import replace
from pathlib import Path

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from army_offence_capability import calculate_army_offensive_output_density
from army_defence_capability import (
    calculate_army_defensive_combat_score,
    calculate_army_defensive_output_density,
)
from i2i_c3_b8a_cohort_intake import FIXTURES, FIXTURE_DIR
from i2i_c3_b8b_mechanical_qualification import load_reference_army_with_platforms
from i2i_c3_b8c_reference_qualification import read_json

ROOT = Path(__file__).resolve().parent
QUALIFICATION = ROOT / "b8c_reference_qualification.json"
BASELINE = DEFAULT_COMBAT_BENCHMARK

# Change ONE opponent dimension at a time, keeping a reproducible baseline.
BENCHMARKS = {
    "baseline_f4_s4_d6": BASELINE,
    "defender_d4": replace(BASELINE, defence=4),
    "defender_d5": replace(BASELINE, defence=5),
    "defender_d7": replace(BASELINE, defence=7),
    "defender_d8": replace(BASELINE, defence=8),
    "opponent_s3": replace(BASELINE, strength=3),
    "opponent_s5": replace(BASELINE, strength=5),
    "opponent_s6": replace(BASELINE, strength=6),
    "opponent_f3": replace(BASELINE, fight=3),
    "opponent_f5": replace(BASELINE, fight=5),
}

METRICS = ("offence_density", "army_survival_density", "per_model_resilience")

def gate_ok(qualification):
    if not isinstance(qualification, dict):
        return False
    rows = qualification.get("armies", ())
    if not isinstance(rows, list):
        return False
    valid = {r.get("army") for r in rows if isinstance(r, dict)
             and r.get("candidate_status") == "provisional_reference"
             and not r.get("candidate_issues")}
    return (
        qualification.get("stage") == "B8-C"
        and qualification.get("status") == "provisional_evidence_qualified"
        and qualification.get("qualification_errors") == []
        and qualification.get("provisional_references") == len(FIXTURES)
        and len(rows) == len(FIXTURES)
        and valid == set(FIXTURES)
        and qualification.get("numerical_calibration_permitted") is False
        and qualification.get("calibration_anchors_approved") is False
    )

def measurements(army, benchmark):
    return {
        "offence_density": float(calculate_army_offensive_output_density(
            army, benchmark)),
        "army_survival_density": float(calculate_army_defensive_output_density(
            army, benchmark, engagements=3, include_resurrection=False)),
        "per_model_resilience": float(calculate_army_defensive_combat_score(
            army, benchmark, engagements=3, include_resurrection=False)),
    }

def rankings(rows, metric):
    ranked = sorted(
        (r for r in rows if metric in r.get("measurements", {})),
        key=lambda r: (-r["measurements"][metric], r["army"]),
    )
    return [r["army"] for r in ranked]

def build_report(qualification, importer=load_reference_army_with_platforms):
    if not gate_ok(qualification):
        return {
            "stage": "I2-I-D2-B1", "status": "blocked_by_qualification_gate",
            "benchmark_results": [], "numerical_calibration_permitted": False,
            "production_scoring_modified": False,
        }
    results = []
    for name, benchmark in BENCHMARKS.items():
        rows = []
        for army_id, (filename, alignment, archetype) in FIXTURES.items():
            try:
                army = importer(FIXTURE_DIR / filename)
                values = measurements(army, benchmark)
                rows.append({"army": army_id, "alignment": alignment,
                             "proposed_archetype": archetype,
                             "models": army.model_count(), "points": army.total_points(),
                             "measurements": values})
            except Exception as exc:
                rows.append({"army": army_id, "error": (
                    type(exc).__name__ + ": " + str(exc))})
        ranks = {m: rankings(rows, m) for m in METRICS}
        results.append({
            "benchmark_id": name,
            "opponent": {
                "fight": benchmark.fight, "strength": benchmark.strength,
                "defence": benchmark.defence, "attacks": benchmark.attacks,
                "wounds": benchmark.wounds,
            },
            "rows": rows, "descending_rankings": ranks,
        })
    baseline_ranks = results[0]["descending_rankings"]
    changes = [
        {"benchmark": item["benchmark_id"],
         "changes": {
             m: item["descending_rankings"][m] != baseline_ranks[m]
             for m in METRICS
         }}
        for item in results[1:]
    ]
    failures = sum("error" in row for r in results for row in r["rows"])
    return {
        "stage": "I2-I-D2-B1",
        "status": "benchmark_sensitivity_complete" if not failures else "incomplete",
        "armies": len(FIXTURES),
        "benchmark_results": results,
        "ranking_changes_from_baseline": changes,
        "metric_units": {
            "offence_density": "offensive_output_per_100_points",
            "army_survival_density": "survival_contribution_per_100_points",
            "per_model_resilience": "mean_model_survival_contribution",
        },
        "errors": failures,
        "analysis_policy": (
            "One opponent characteristic varied at a time; all values "
            "read-only diagnostic outputs. No resurrection. "
            "No weapon, terrain or shooting changes tested in B1."
        ),
        "numerical_calibration_permitted": False,
        "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }

if __name__ == "__main__":
    if not QUALIFICATION.exists():
        print(json.dumps({"stage":"I2-I-D2-B1","status":"missing_qualification_evidence"},
                         indent=2))
        raise SystemExit(2)
    print(json.dumps(build_report(read_json(QUALIFICATION)), indent=2))
