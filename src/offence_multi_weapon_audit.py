"""Project Palantír — DEV-082-A3-2G-1 multi-weapon read-only audit.

Author: Edward Turns (Project Lead)
Audits catalogued alternatives and their existing A3-2D conditional outcomes.
A recognised wargear ID is NOT proof of legal use in any battlefield state.
No tactical weapon selection, new combat probability or production score.
"""
from __future__ import annotations

from math import isfinite
from collections import Counter


STATES = ("uncharged_probability", "charged_probability",
          "eligible_cavalry_charge_probability")


def audit_multi_weapon_report(report: dict, *, key: str) -> dict:
    if report.get("stage") != "DEV-082-A3-2D":
        raise ValueError("Expected read-only A3-2D weapon report")
    if (report.get("candidate_raw_density") is not None
            or report.get("comparable") is not False
            or report.get("production_scoring_changed") is not False
            or report.get("calibration_changed") is not False):
        raise ValueError("Weapon audit must not alter scoring or calibration")
    rows = report.get("profile_rows")
    if not isinstance(rows, list):
        raise ValueError("Missing profile rows")
    examined = 0
    affected = 0
    audited = []
    status_counts = Counter()
    for row in rows:
        n = row.get("quantity")
        if type(n) is not int or n <= 0:
            raise ValueError("Invalid quantity")
        examined += n
        w = row.get("weapon_options")
        if not isinstance(w, dict):
            raise ValueError("Missing weapon evidence")
        status = w.get("status")
        status_counts[status] += n
        if status != "multiple_options":
            continue
        affected += n
        ids = w.get("candidate_weapon_ids")
        outcomes = w.get("explicit_option_outcomes")
        if not isinstance(ids, list) or len(ids) < 2 or len(ids) != len(set(ids)):
            raise ValueError("Multiple weapon options require distinct candidates")
        if not isinstance(outcomes, list) or {x.get("weapon_id") for x in outcomes} != set(ids):
            raise ValueError("Each recognised alternative needs its own evidence")
        alternatives = []
        differences = {}
        for option in outcomes:
            values = {}
            for state in STATES:
                v = option.get(state)
                if type(v) not in (float, int) or not isfinite(v) or not 0 <= v <= 1:
                    raise ValueError("Invalid alternative probability")
                values[state] = v
            alternatives.append({"weapon_id": option["weapon_id"],
                                 "conditional_probabilities": values,
                                 "battlefield_legality": "not_verified",
                                 "player_choice": "not_inferred"})
        for state in STATES:
            values = [option["conditional_probabilities"][state] for option in alternatives]
            differences[state] = {
                "minimum": min(values), "maximum": max(values),
                "spread": max(values) - min(values),
                "outcomes_differ": max(values) - min(values) > 1e-12,
            }
        audited.append({
            "profile_id": row["profile_id"], "quantity": n,
            "candidate_weapon_ids": list(ids), "alternatives": alternatives,
            "outcome_comparison": differences,
            "selection_status": "requires_legal_option_and_tactical_policy",
            "legal_option_verified": False,
        })
    expected = report.get("fielded_models")
    if examined != expected:
        raise ValueError("Profile count mismatch")
    if affected != report.get("weapon_model_status_counts", {}).get("multiple_options", 0):
        raise ValueError("Affected model total differs from A3-2D")
    return {
        "key": key, "status": "audited", "models": examined,
        "multiple_weapon_models": affected,
        "multiple_weapon_profiles": len(audited),
        "weapon_status_model_counts": dict(sorted(status_counts.items())),
        "profile_audits": audited,
        "legality_verified": False,
        "automatic_selection_made": False,
        "candidate_raw_density": None, "comparable": False,
        "production_scoring_changed": False, "calibration_changed": False,
    }


def build_multi_weapon_cohort(*, fixtures, loader, weapon_reporter) -> dict:
    """Run every expected cohort fixture; never hide an incomplete army."""
    rows = []
    for key, path in fixtures:
        try:
            army = loader(path)
            row = audit_multi_weapon_report(weapon_reporter(army), key=key)
        except Exception as exc:
            rows.append({"key": key, "status": "blocked",
                         "reason": f"{type(exc).__name__}: {exc}"})
        else:
            rows.append(row)
    validated = [row for row in rows if row["status"] == "audited"]
    return {
        "stage": "DEV-082-A3-2G-1",
        "status": "complete" if len(validated) == len(rows) and rows else "incomplete",
        "armies_audited": len(validated),
        "armies_expected": len(rows),
        "multi_weapon_models": sum(row["multiple_weapon_models"] for row in validated),
        "multi_weapon_profiles": sum(row["multiple_weapon_profiles"] for row in validated),
        "rows": rows,
        "scope": "catalogued_weapon_alternatives_not_legal_use",
        "production_scoring_changed": False, "calibration_changed": False,
        "candidate_raw_density": None, "dashboard_score": None,
        "scenario_score": None,
    }
