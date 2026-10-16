"""DEV-077S-I2-I-D2-C — read-only cross-metric/archetype consistency.

Consumes the existing six-army evidence files. Descriptive correlations and
archetype expectations are diagnostics, never calibration weights or approvals.
"""
from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
FILES = {
    "qualification": "b8c_reference_qualification.json",
    "d1": "i2i_d1_measurement_matrix.json",
    "d2a": "i2i_d2a_distribution_size_report.json",
    "combat": "i2i_d2b1_combat_benchmark_sensitivity.json",
    "movement_shooting": "i2i_d2b2_mobility_shooting_sensitivity.json",
}

METRICS = (
    "offence_density", "army_survival_density", "per_model_resilience",
    "open_ground_mobility", "stationary_shooting", "courage_reliability",
)
# Hypotheses for descriptive review, not official classification or pass criteria.
HYPOTHESES = {
    "dol_guldur": ("per_model_resilience", "Elite magic: individual resilience; magic is outside this six-metric audit"),
    "azogs_hunters": ("open_ground_mobility", "Mobile assault: open-ground mobility"),
    "pits_of_dol_guldur": ("offence_density", "Mixed assault: offensive output density"),
    "rangers_of_mirkwood": ("stationary_shooting", "Mass shooting: stationary ranged output"),
    "five_armies": ("army_survival_density", "Combined arms: army staying power is only one aspect"),
    "iron_hills": ("per_model_resilience", "Armoured defence: individual resilience, not necessarily total density"),
}


def read_json(path: Path):
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return json.loads(raw.decode("utf-16"))
    if raw[:4].count(b"\x00"):
        return json.loads(raw.decode("utf-16-le"))
    return json.loads(raw.decode("utf-8-sig"))


def pearson(a, b):
    """Small-sample descriptive Pearson r; undefined correlation is None."""
    if len(a) != len(b) or len(a) < 2:
        return None
    ma, mb = mean(a), mean(b)
    aa = sum((x - ma) ** 2 for x in a)
    bb = sum((y - mb) ** 2 for y in b)
    if aa <= 1e-24 or bb <= 1e-24:
        return None
    return max(-1., min(1., sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(aa * bb)))


def check_inputs(data):
    q, d1, a, combat, terrain = (data[k] for k in FILES)
    errors = []
    if q.get("stage") != "B8-C" or q.get("status") != "provisional_evidence_qualified" or q.get("provisional_references") != 6:
        errors.append("reference_qualification_invalid")
    if q.get("numerical_calibration_permitted") is not False or q.get("calibration_anchors_approved") is not False:
        errors.append("qualification_approval_gate_invalid")
    expected = set(HYPOTHESES)
    if {x.get("army") for x in q.get("armies", [])} != expected:
        errors.append("reference_identities_invalid")
    for k, stage, states in (
        ("d1", "I2-I-D1", {"matrix_complete"}),
        ("d2a", "I2-I-D2-A", {"distribution_audit_complete"}),
        ("combat", "I2-I-D2-B1", {"benchmark_sensitivity_complete"}),
        ("movement_shooting", "I2-I-D2-B2", {"sensitivity_complete"}),
    ):
        if data[k].get("stage") != stage or data[k].get("status") not in states:
            errors.append(f"{k}_stage_or_status_invalid")
        if data[k].get("numerical_calibration_permitted") is not False:
            errors.append(f"{k}_calibration_gate_invalid")
    for k, rows in (("d1", d1.get("rows", [])), ("movement_shooting", terrain.get("rows", []))):
        ids = [x.get("army") for x in rows]
        if len(ids) != 6 or set(ids) != expected or len(set(ids)) != 6:
            errors.append(f"{k}_rosters_mismatch")
    b = combat.get("benchmark_results", [])
    if not b or b[0].get("benchmark_id") != "baseline_f4_s4_d6" or len(b[0].get("rows", [])) != 6:
        errors.append("combat_baseline_missing")
    elif {r.get("army") for r in b[0]["rows"]} != expected:
        errors.append("combat_rosters_mismatch")
    return errors


def build_report(data):
    errors = check_inputs(data)
    if errors:
        return {"stage": "I2-I-D2-C", "status": "blocked_evidence", "errors": errors,
                "numerical_calibration_permitted": False, "production_scoring_modified": False}
    d1 = {r["army"]: r for r in data["d1"]["rows"]}
    terrain = {r["army"]: r for r in data["movement_shooting"]["rows"]}
    combat = {r["army"]: r for r in data["combat"]["benchmark_results"][0]["rows"]}
    rows = []
    for army in HYPOTHESES:
        original = d1[army]["measurements"]
        values = {
            "offence_density": original["offence"]["value"],
            "army_survival_density": combat[army]["measurements"]["army_survival_density"],
            "per_model_resilience": combat[army]["measurements"]["per_model_resilience"],
            "open_ground_mobility": terrain[army]["measurements"]["mobility"]["open_ground"],
            "stationary_shooting": terrain[army]["measurements"]["shooting"]["stationary"],
            "courage_reliability": original["courage"]["value"],
        }
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for v in values.values()):
            return {"stage": "I2-I-D2-C", "status": "blocked_evidence", "errors": [f"nonfinite_or_missing_{army}"],
                    "numerical_calibration_permitted": False, "production_scoring_modified": False}
        if not math.isclose(values["army_survival_density"], original["defence"]["value"], rel_tol=1e-9, abs_tol=1e-10):
            errors.append(f"defence_baseline_mismatch_{army}")
        if not math.isclose(values["stationary_shooting"], original["shooting"]["value"], rel_tol=1e-9, abs_tol=1e-10):
            errors.append(f"shooting_baseline_mismatch_{army}")
        if not math.isclose(values["open_ground_mobility"], original["mobility"]["value"], rel_tol=1e-9, abs_tol=1e-10):
            errors.append(f"mobility_baseline_mismatch_{army}")
        rows.append({"army": army, "models": terrain[army]["measurements"]["model_count"],
                     "points": terrain[army]["measurements"]["army_points"], "values": values})
    if errors:
        return {"stage": "I2-I-D2-C", "status": "blocked_evidence", "errors": errors,
                "numerical_calibration_permitted": False, "production_scoring_modified": False}
    pairwise = []
    for x, y in combinations(METRICS, 2):
        corr = pearson([r["values"][x] for r in rows], [r["values"][y] for r in rows])
        pairwise.append({"metric_a": x, "metric_b": y, "pearson_r": corr,
                         "absolute_r": abs(corr) if corr is not None else None,
                         "interpretation": "descriptive_only_n_6"})
    pairwise.sort(key=lambda r: -(r["absolute_r"] if r["absolute_r"] is not None else -1))
    rankings = {m: [r["army"] for r in sorted(rows, key=lambda r: (-r["values"][m], r["army"]))] for m in METRICS}
    hypotheses = []
    for army, (metric, rationale) in HYPOTHESES.items():
        rank = rankings[metric].index(army) + 1
        hypotheses.append({"army": army, "proposed_archetype": next(a["proposed_archetype"] for a in data["d1"]["rows"] if a["army"] == army),
                           "diagnostic_metric": metric, "observed_rank": rank,
                           "of_armies": 6, "interpretation": rationale,
                           "approved": False})
    return {
        "stage": "I2-I-D2-C", "status": "cross_metric_audit_complete", "errors": [],
        "armies": 6, "metric_count": len(METRICS), "metrics": list(METRICS),
        "rankings": rankings, "pairwise_correlations": pairwise,
        "model_count_correlations": {m: pearson([r["models"] for r in rows], [r["values"][m] for r in rows]) for m in METRICS},
        "archetype_hypotheses": hypotheses,
        "derived_metric_dependency": {
            "metrics": ["army_survival_density", "per_model_resilience"],
            "relationship": "survival_density = per_model_resilience * model_count * 100 / points",
            "double_counting_warning": True,
            "treatment": "show_separately; do_not_combine_as_independent_weighted_evidence",
        },
        "exclusions": [
            "Mirkwood Woodland Creature terrain-specific mechanics not qualified: D2-B2 movement values are generic terrain only",
            "Iron Hills Chariot platform physical movement and combat behaviour not qualified",
            "Magic, Control, Command, Objective and Hero Hunting excluded, not zero",
            "Archetypes not independently approved; hypotheses are explanatory only",
            "Six chosen reference armies do not support population-level inference",
        ],
        "calibration_anchors_approved": False, "numerical_calibration_permitted": False,
        "production_scoring_modified": False,
    }


def main():
    missing = [name for name in FILES.values() if not (ROOT / name).is_file()]
    if missing:
        print(json.dumps({"stage": "I2-I-D2-C", "status": "missing_evidence_files", "missing": missing}, indent=2))
        raise SystemExit(2)
    report = build_report({key: read_json(ROOT / filename) for key, filename in FILES.items()})
    print(json.dumps(report, indent=2))
    if report["status"] != "cross_metric_audit_complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
