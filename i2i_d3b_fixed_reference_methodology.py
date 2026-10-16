"""DEV-077S-I2-I-D3-B: read-only fixed-reference calibration governance.

Outputs an evidence-grounded methodology and gate ledger; deliberately DOES NOT
derive, fit, propose numerical anchor values, or issue an approval.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "b8c": ("B8-C", "provisional_evidence_qualified"),
    "d2c": ("I2-I-D2-C", "cross_metric_audit_complete"),
    "d3a": ("I2-I-D3-A", "illustrative_scales_complete"),
}
SOURCE_FILES = {
    "b8c": "b8c_reference_qualification.json",
    "d2c": "i2i_d2c_cross_metric_archetype_report.json",
    "d3a": "i2i_d3a_candidate_scales.json",
}
SIX_METRICS = (
    "offence_density", "army_survival_density", "per_model_resilience",
    "open_ground_mobility", "stationary_shooting", "courage_reliability",
)
DEPENDENT_PAIR = ("army_survival_density", "per_model_resilience")


def read_json(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return json.loads(raw.decode("utf-16"))
    if b"\x00" in raw[:4]:
        return json.loads(raw.decode("utf-16-le"))
    return json.loads(raw.decode("utf-8-sig"))


def source_gate(sources: dict) -> list[str]:
    problems = []
    for name, (stage, status) in EXPECTED.items():
        report = sources.get(name)
        if not isinstance(report, dict):
            problems.append(f"{name}: missing or invalid report")
            continue
        if report.get("stage") != stage or report.get("status") != status:
            problems.append(f"{name}: stage or status mismatch")
        if report.get("calibration_anchors_approved") is not False:
            problems.append(f"{name}: unexpected anchor approval state")
        if report.get("numerical_calibration_permitted") is not False:
            problems.append(f"{name}: unexpected calibration permission state")
        if report.get("production_scoring_modified") is not False:
            problems.append(f"{name}: production scoring not proven unchanged")
    b8c, d2c, d3a = (sources.get(k, {}) for k in ("b8c", "d2c", "d3a"))
    if all(isinstance(x, dict) for x in (b8c, d2c, d3a)):
        b8c_names = {r.get("army") for r in b8c.get("armies", ())
                     if isinstance(r, dict)
                     and r.get("candidate_status") == "provisional_reference"}
        d3a_names = set(d3a.get("armies", ()))
        if len(b8c_names) != 6 or b8c_names != d3a_names or d2c.get("armies") != 6:
            problems.append("six-army provisional cohort mismatch")
        if set(d3a.get("scales", {})) != set(SIX_METRICS):
            problems.append("D3-A metric set incomplete or unexpected")
        derived = d2c.get("derived_metric_dependency", {})
        if set(derived.get("metrics", ())) != set(DEPENDENT_PAIR):
            problems.append("Defence dependency not documented")
        if derived.get("double_counting_warning") is not True:
            problems.append("Defence double-counting safeguard absent")
        if d2c.get("errors") != []:
            problems.append("D2-C reports errors")
        if d3a.get("composite_score_calculated") is not False:
            problems.append("D3-A composite calculation disallowed")
    return problems


def method_specifications():
    return {
        "candidate": "fixed_reference_piecewise_monotone",
        "status": "design_only_not_selected",
        "metric_direction": "higher_is_better",
        "reference_policy": [
            "Use frozen, externally qualified reference cases and mechanical contexts.",
            "Record anchor values with units, provenance, benchmark settings and exclusions.",
            "Never refit reference anchors when a user adds a list.",
            "Quantify benchmark and roster sensitivity before selecting reference values.",
            "Keep missing or unsupported mechanics explicitly not_evaluated, never zero."
        ],
        "candidate_anchor_record_fields": [
            "metric_id", "metric_version", "benchmark_version", "unit",
            "reference_id", "reference_value", "evidence_source",
            "validation_status", "approval_id", "effective_release",
        ],
        "anchor_values": None,
        "anchor_version": None,
        "proposed_function": (
            "monotonic, documented, bounded mapping through fixed approved references; "
            "do not extrapolate unvalidated endpoints"
        ),
        "versioning": {
            "schema_version": "D3-B-design-1",
            "immutable_after_approval": [
                "metric_version", "benchmark_version", "anchor_version",
                "reference_value", "unit", "mapping_parameters",
            ],
            "revision_requires": [
                "new version", "comparison to previous frozen reference cases",
                "independent approval", "regression and release notes",
            ],
        },
    }


def approval_gates():
    return [
        {"id": "G1", "name": "Representative reference population",
         "state": "pending", "evidence_needed": (
             "More independently reviewed army lists spanning points, "
             "faction, size, equipment, role and scenario diversity")},
        {"id": "G2", "name": "Rule and context qualification",
         "state": "pending", "evidence_needed": (
             "Woodland Creature terrain context, Iron Hills Chariot physical mechanics; "
             "conditional Magic, Control, Command, Objective and Hero Hunting contexts")},
        {"id": "G3", "name": "Metric semantics and benchmark freeze",
         "state": "pending", "evidence_needed": (
             "Approve common benchmark assumptions, units, metric direction, "
             "and context treatment including stationary/moving shooting")},
        {"id": "G4", "name": "Independent anchor selection",
         "state": "pending", "evidence_needed": (
             "Traceable external or validated mechanical exemplars, "
             "numerical candidate thresholds and independent sign-off")},
        {"id": "G5", "name": "Dependency and weighting safeguards",
         "state": "pending", "evidence_needed": (
             "Prevent collective survival and per-model resilience from "
             "being treated as independent weighted evidence")},
        {"id": "G6", "name": "Holdout, stability and regression",
         "state": "pending", "evidence_needed": (
             "Unseen lists, adversarial cases, new-cohort invariance, "
             "sensitivity regression, and production compatibility")},
        {"id": "G7", "name": "Release authorisation",
         "state": "pending", "evidence_needed": (
             "Documented user approval of selected scale, version and rollout")},
    ]


def build_report(sources: dict) -> dict:
    problems = source_gate(sources)
    return {
        "stage": "I2-I-D3-B",
        "status": "methodology_documented" if not problems else "blocked_by_evidence_gate",
        "source_gate_errors": problems,
        "basis": {name: {"stage": EXPECTED[name][0], "status": EXPECTED[name][1],
                         "file": SOURCE_FILES[name]} for name in EXPECTED},
        "method": method_specifications(),
        "covered_metrics": list(SIX_METRICS),
        "dependency_policy": {
            "measurements": list(DEPENDENT_PAIR),
            "relationship": (
                "army_survival_density = per_model_resilience * model_count * 100 / points"
            ),
            "independent_weighting_allowed": False,
            "both_may_be_displayed": True,
        },
        "approval_gates": approval_gates(),
        "unresolved_exclusions": [
            "Mirkwood Woodland Creature difficult-terrain integration",
            "Iron Hills Chariot physical mechanics",
            "Conditional Magic, Control, Command, Objective and Hero Hunting",
            "Six reference armies not representative for anchor fitting",
        ],
        "candidate_anchor_values": None,
        "approved_method": None,
        "calibration_anchors_approved": False,
        "numerical_calibration_permitted": False,
        "composite_score_calculated": False,
        "production_scoring_modified": False,
    }


def load_sources(root: Path = ROOT) -> dict:
    return {name: read_json(root / filename)
            for name, filename in SOURCE_FILES.items()}


if __name__ == "__main__":
    try:
        data = build_report(load_sources())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        data = build_report({})
        data["source_gate_errors"].append(f"input: {type(exc).__name__}: {exc}")
    print(json.dumps(data, indent=2))
    if data["status"] != "methodology_documented":
        raise SystemExit(2)
