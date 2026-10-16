"""DEV-077S-I2-I-D3-C — evidence-backed, read-only calibration readiness.

This is a gate ledger, not a calibration engine or approval authority.
D3-B documented seven gates as pending; D3-C must never imply that
successfully parsing evidence or passing tests approves them.
"""
from __future__ import annotations

import json
from pathlib import Path

from i2i_d3b_fixed_reference_methodology import read_json, source_gate

ROOT = Path(__file__).resolve().parent
INPUTS = {
    "b8c": "b8c_reference_qualification.json",
    "d2c": "i2i_d2c_cross_metric_archetype_report.json",
    "d3a": "i2i_d3a_candidate_scales.json",
    "d3b": "i2i_d3b_fixed_reference_methodology.json",
}

GATES = {
    "G1": ("Representative reference population", "outstanding", "Six deliberately selected armies are provisional, not representative of MESBG."),
    "G2": ("Rule and context qualification", "conditional", "Woodland Creature terrain, Chariot physical mechanics and contextual capabilities require independent qualification."),
    "G3": ("Metric semantics and benchmark freeze", "conditional", "Six mechanical measurements exist, but benchmark settings, assumptions and version remain unapproved."),
    "G4": ("Independent anchor selection", "outstanding", "No numerical anchors, independent provenance or sign-off exist."),
    "G5": ("Dependency and weighting safeguards", "validated", "Both Defence indicators have a documented algebraic dependency and a no-independent-weighting policy; implementation enforcement remains pending."),
    "G6": ("Holdout, stability and regression", "outstanding", "No independently qualified holdout population or versioned production calibration regression exists."),
    "G7": ("Release authorisation", "outstanding", "No approved scale, signed gate record or release decision exists."),
}


def assess(evidence: dict) -> dict:
    """Report what is documented, never grant formal gate approval."""
    problems = []
    for key in INPUTS:
        if not isinstance(evidence.get(key), dict):
            problems.append(f"{key}: missing or invalid report")
    if not problems:
        problems.extend(source_gate(evidence))
        d3b = evidence["d3b"]
        if d3b.get("stage") != "I2-I-D3-B" or d3b.get("status") != "methodology_documented":
            problems.append("d3b: methodology stage/status mismatch")
        if d3b.get("source_gate_errors") != []:
            problems.append("d3b: source evidence errors present")
        for field in ("calibration_anchors_approved", "numerical_calibration_permitted", "production_scoring_modified", "composite_score_calculated"):
            if d3b.get(field) is not False:
                problems.append(f"d3b: invalid {field} state")
        method = d3b.get("method", {})
        if method.get("anchor_values", object()) is not None or d3b.get("candidate_anchor_values", object()) is not None:
            problems.append("d3b: numerical anchors unexpectedly supplied")
        if d3b.get("approved_method", object()) is not None:
            problems.append("d3b: method unexpectedly approved")
        dependency = d3b.get("dependency_policy", {})
        if dependency.get("independent_weighting_allowed") is not False:
            problems.append("d3b: Defence dependency safeguard missing")
        source_gates = d3b.get("approval_gates", [])
        if not isinstance(source_gates, list) or {g.get("id") for g in source_gates if isinstance(g, dict)} != set(GATES):
            problems.append("d3b: expected seven gate definitions missing")
        elif any(g.get("state") != "pending" for g in source_gates):
            problems.append("d3b: pre-existing gate unexpectedly marked approved")
    gates = []
    for key, (name, evidence_class, reason) in GATES.items():
        gates.append({
            "id": key,
            "name": name,
            "evidence_class": evidence_class if not problems else "unverified",
            "formal_approval": "pending",
            "evidence_summary": reason,
            "next_action": {
                "G1": "Qualify more independent army rosters and holdouts.",
                "G2": "Resolve named exceptions and context-dependent capabilities.",
                "G3": "Approve metric meanings, units, benchmarks and frozen versions.",
                "G4": "Document and independently justify fixed numerical anchors.",
                "G5": "Enforce the algebraic Defence dependency in any future composite scorer.",
                "G6": "Run unseen-list, scaling invariance, sensitivity and backwards-compatibility tests.",
                "G7": "Obtain explicit approval of method, anchor version and release plan.",
            }[key],
        })
    return {
        "stage": "I2-I-D3-C",
        "status": "readiness_audit_complete" if not problems else "blocked_by_evidence_gate",
        "source_gate_errors": problems,
        "gates": gates,
        "gate_counts": {
            "formally_approved": 0,
            "pending": len(gates),
            "evidence_validated": sum(g["evidence_class"] == "validated" for g in gates),
            "evidence_conditional": sum(g["evidence_class"] == "conditional" for g in gates),
            "evidence_outstanding": sum(g["evidence_class"] == "outstanding" for g in gates),
        },
        "release_readiness": "not_ready",
        "approved_method": None,
        "numerical_anchors": None,
        "calibration_anchors_approved": False,
        "numerical_calibration_permitted": False,
        "composite_score_calculated": False,
        "production_scoring_modified": False,
        "limitations": [
            "Evidence classifications describe documentation, not formal gate approvals.",
            "Six-army cohort not representative; no population thresholds inferred.",
            "Magic, Control, Command, Objective and Hero Hunting excluded, not assigned zero.",
            "Woodland Creature terrain and Iron Hills Chariot physical effects unresolved.",
            "No numerical anchors or new scoring implementation is authorised.",
        ],
    }


def load_evidence(root: Path = ROOT) -> dict:
    return {key: read_json(root / filename) for key, filename in INPUTS.items()}


if __name__ == "__main__":
    try:
        result = assess(load_evidence())
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        result = assess({})
        result["source_gate_errors"].append(f"input error: {type(exc).__name__}: {exc}")
    print(json.dumps(result, indent=2))
    if result["status"] != "readiness_audit_complete":
        raise SystemExit(2)
