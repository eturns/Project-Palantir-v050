"""B8-B3 read-only roster special-rule exposure and verification queue.

This audit detects which configured rules are present on each reference roster.
It deliberately does NOT equate a rule assignment with a working mechanic.
Verification requires a separately reviewed evidence registry in a later phase.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path

from i2i_c3_b8a_cohort_intake import FIXTURES, FIXTURE_DIR
from i2i_c3_b8b_mechanical_qualification import audit as equipment_audit
from i2i_mirkwood_b5_shooting_evidence import load_reference_army


def roster_rule_exposure(army):
    """Extract per-model rule assignment exposure from actual configured models."""
    by_rule = defaultdict(lambda: {"model_count": 0, "profiles": Counter(),
                                   "parameters": set()})
    count = 0
    for fielded in army.fielded_models():
        configured = fielded.configured_profile
        if configured is None:
            continue
        count += 1
        # Deduplicate repeat assignments on the same model, not across models.
        observed = set()
        for assignment in configured.effective_special_rules:
            rule = assignment.rule
            key = (str(rule.id), str(assignment.parameter))
            if key in observed:
                continue
            observed.add(key)
            slot = by_rule[str(rule.id)]
            slot["model_count"] += 1
            slot["profiles"][str(configured.profile.id)] += 1
            if assignment.parameter is not None:
                slot["parameters"].add(str(assignment.parameter))
    return count, [
        {"rule_id": rid, "affected_models": data["model_count"],
         "profiles": dict(sorted(data["profiles"].items())),
         "parameters": sorted(data["parameters"]),
         "mechanical_verification": "not_evaluated",
         "evidence": None}
        for rid, data in sorted(by_rule.items(),
                                key=lambda item: (-item[1]["model_count"], item[0]))
    ]


def build_report(*, importer=load_reference_army, fixture_dir=FIXTURE_DIR,
                 equipment_report=None):
    if equipment_report is None:
        equipment_report = equipment_audit()
    equipment = {row["army"]: row for row in equipment_report["results"]}
    results = []
    all_rules = defaultdict(lambda: {"armies": set(), "model_exposures": 0})
    for key, (filename, alignment, proposed_archetype) in FIXTURES.items():
        row = {"army": key, "alignment": alignment,
               "proposed_archetype": proposed_archetype,
               "status": "blocked", "issues": [], "models_scanned": None,
               "rules": [], "unverified_rule_types": 0,
               "special_rules_approved": False}
        eq = equipment.get(key)
        if not eq or eq["status"] != "option_audit_passed":
            row["issues"].append("equipment_qualification_missing")
            results.append(row)
            continue
        try:
            path = Path(fixture_dir) / filename
            army = importer(path)
            row["models_scanned"], row["rules"] = roster_rule_exposure(army)
            row["unverified_rule_types"] = len(row["rules"])
            row["status"] = "inventory_complete_review_pending"
            for item in row["rules"]:
                agg = all_rules[item["rule_id"]]
                agg["armies"].add(key)
                agg["model_exposures"] += item["affected_models"]
        except Exception as exc:
            row["issues"].append(f"rule_inventory_failed:{type(exc).__name__}:{exc}")
        results.append(row)
    ranked = sorted(({
        "rule_id": rid, "armies_affected": len(data["armies"]),
        "affected_army_keys": sorted(data["armies"]),
        "model_exposures": data["model_exposures"],
        "verification_priority": "review_required",
    } for rid, data in all_rules.items()),
        key=lambda r: (-r["armies_affected"], -r["model_exposures"], r["rule_id"]))
    return {"stage": "B8-B3", "scope": "actual_profile_special_rule_exposure",
            "armies": results, "cross_army_verification_queue": ranked,
            "armies_inventoried": sum(r["status"] == "inventory_complete_review_pending"
                                     for r in results),
            "candidates": len(results),
            "qualification_note": "A detected rule is not proof of execution. "
                                  "Missing rule assignments cannot be detected without "
                                  "an independent rulebook-to-profile comparison.",
            "full_special_rules_approved": False,
            "archetype_review_approved": False,
            "calibration_anchors_approved": False,
            "production_scoring_modified": False}


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
