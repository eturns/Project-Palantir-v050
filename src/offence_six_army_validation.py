"""Project Palantír — DEV-082-A3-2F six-army Offence cohort validation.

Author: Edward Turns (Project Lead)

Aggregates read-only A3-2E reports. Keeps all probabilities conditional.
Does not calculate replacement Offence density, refit calibration, or
change scenario/production metrics.
"""
from __future__ import annotations

from collections import Counter
from math import isfinite

COHORT_FIXTURES = (
    ("dol_guldur", "dol_guldur_700.json"),
    ("azogs_hunters", "azogs-hunters.json"),
    ("pits_of_dol_guldur", "pits-of-dol-guldur.json"),
    ("rangers_of_mirkwood", "rangers-of-mirkwood.json"),
    ("five_armies", "five_armies_cal.json"),
    ("iron_hills", "iron-hills-cal.json"),
)


def _number(value, name, *, probability=False):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (probability and value > 1):
        raise ValueError(f"{name} out of range")
    return value


def summarise_army_offence_report(key: str, report: dict) -> dict:
    """Validate and summarise a single imported army's A3-2E evidence."""
    if not isinstance(key, str) or not key:
        raise ValueError("A nonblank cohort key is required")
    if not isinstance(report, dict) or report.get("stage") != "DEV-082-A3-2E":
        raise ValueError("Requires an A3-2E real-army report")
    if report.get("candidate_raw_density") is not None or report.get("comparable") is not False:
        raise ValueError("Replacement Offence density is not qualified")
    if report.get("production_scoring_changed") is not False or report.get("calibration_changed") is not False:
        raise ValueError("Read-only evidence contract violated")
    if report.get("trapping_frequency_assumed") is not False:
        raise ValueError("Trapping frequency must not be inferred")
    points = _number(report.get("army_points"), "army_points")
    legacy = _number(report.get("legacy_raw_density"), "legacy_raw_density")
    models = report.get("fielded_models")
    if type(models) is not int or models < 1:
        raise ValueError("fielded_models must be positive integer")
    rows = report.get("profile_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Profile rows missing")
    quantity_total, paired, unresolved = 0, 0, 0
    weapon_statuses, trap_statuses, conditional_effects = Counter(), Counter(), Counter()
    unknowns = Counter()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Malformed profile row")
        n = row.get("quantity")
        if type(n) is not int or n < 1:
            raise ValueError("Invalid fielded profile quantity")
        quantity_total += n
        weapons = row.get("weapon_options")
        if not isinstance(weapons, dict):
            raise ValueError("Weapon qualification missing")
        ws = weapons.get("status")
        if not isinstance(ws, str) or not ws:
            raise ValueError("Weapon status missing")
        weapon_statuses[ws] += n
        trap_status = row.get("trapping_benchmark_status")
        if not isinstance(trap_status, str) or not trap_status:
            raise ValueError("Trapping qualification status missing")
        trap_statuses[trap_status] += n
        trap = row.get("trapping_benchmark")
        if trap_status == "paired_conditional_outcomes":
            if not isinstance(trap, dict):
                raise ValueError("Missing paired trapping evidence")
            if trap.get("trapping_frequency") is not None or trap.get("trapping_frequency_inferred") is not False:
                raise ValueError("Trapping frequency was invented")
            states = trap.get("conditional_combat_states")
            if not isinstance(states, list) or len(states) != 3:
                raise ValueError("Expected three conditional combat states")
            for state in states:
                for k in ("untrapped_probability", "trapped_probability"):
                    _number(state.get(k), k, probability=True)
                p0, p1 = state["untrapped_probability"], state["trapped_probability"]
                delta = _number(state.get("absolute_improvement"), "absolute_improvement")
                if abs((p1-p0) - delta) > 1e-9:
                    raise ValueError("Trapping improvement inconsistent")
                if p1 + 1e-12 < p0:
                    raise ValueError("Trapping reduced probability")
                if delta > 1e-12:
                    conditional_effects[state.get("state", "unknown")] += n
            paired += n
        else:
            if trap is not None:
                raise ValueError("Unqualified trapping result was supplied")
            unresolved += n
        qualifications = row.get("qualification", {})
        if not isinstance(qualifications, dict):
            raise ValueError("Malformed qualification")
        for field, evidence in qualifications.items():
            if isinstance(evidence, dict) and evidence.get("status") == "unresolved":
                unknowns[field] += n

    if quantity_total != models or paired + unresolved != models:
        raise ValueError("Model population does not reconcile")
    if dict(sorted(trap_statuses.items())) != report.get("trapping_benchmark_model_status_counts"):
        raise ValueError("Trapping status summary mismatch")
    return {
        "key": key, "status": "validated",
        "points": points, "models": models,
        "legacy_raw_density": legacy,
        "conditional_trapping_models": paired,
        "trapping_unresolved_models": unresolved,
        "weapon_status_model_counts": dict(sorted(weapon_statuses.items())),
        "trapping_status_model_counts": dict(sorted(trap_statuses.items())),
        "unresolved_condition_model_counts": dict(sorted(unknowns.items())),
        "trapping_effect_model_counts_by_state": dict(sorted(conditional_effects.items())),
        "candidate_raw_density": None,
        "comparable": False,
    }


def build_six_army_offence_cohort(*, fixture_dir, loader, reporter) -> dict:
    """Process all six fixtures independently; never conceal an army failure."""
    from pathlib import Path
    root = Path(fixture_dir)
    rows = []
    for key, name in COHORT_FIXTURES:
        path = root / name
        if not path.is_file():
            rows.append({"key": key, "fixture": name, "status": "blocked",
                         "reason": "fixture_missing"})
            continue
        try:
            army = loader(path)
            report = reporter(army)
            summary = summarise_army_offence_report(key, report)
        except Exception as error:
            # Keep a failed army visible, without fabricating a successful result.
            rows.append({"key": key, "fixture": name, "status": "blocked",
                         "reason": f"{type(error).__name__}: {error}"})
            continue
        rows.append({"fixture": name, **summary})
    complete = sum(row["status"] == "validated" for row in rows)
    return {
        "stage": "DEV-082-A3-2F",
        "validation_status": "six_armies_validated" if complete == 6 else "incomplete",
        "armies_validated": complete,
        "armies_expected": 6,
        "rows": rows,
        "benchmark": "ordinary_single_wound",
        "comparison_type": "conditional_evidence_only_no_weighted_army_density",
        "candidate_raw_density": None,
        "calibration_changed": False,
        "production_scoring_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
