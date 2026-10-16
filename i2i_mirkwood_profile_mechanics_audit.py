"""Read-only profile-rule implementation audit for DEV-077S-I2-I-C3-D7-B4-B4-B.

This is a source-presence audit, not proof that code is wired through all
analysis contexts. It never modifies production files or scoring.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Each evidence item must be verified by an explicit identifier in source code.
EVIDENCE = {
    "SHARPSHOOTER": [("src/sharpshooter.py", "SHARPSHOOTER_RULE_ID")],
    "EXPERT_SHOT": [("src/shooting_attack_count.py", "EXPERT_SHOT_RULE_ID")],
    "DEADLY_SHOT": [
        ("src/shooting_attack_count.py", "DEADLY_SHOT_RULE_ID"),
        ("src/shooting_to_hit_modifier.py", "DEADLY_SHOT_RULE_ID"),
        ("src/shooting_eligibility.py", "DEADLY_SHOT_RULE_ID"),
    ],
    "PINPOINT_SHOT": [],
    "WOODLAND_CREATURE": [],
    "KNIFE_FIGHTER": [],
    "BLADE_MISTRESS": [],
    "VENGEFUL_FURY": [],
    "LEADER_PALACE_GUARD": [],
}

def audit(root: Path = ROOT) -> dict:
    results = {}
    for rule_id, evidence in EVIDENCE.items():
        found, missing = [], []
        for relative, marker in evidence:
            path = root / relative
            if path.is_file() and marker in path.read_text(encoding="utf-8"):
                found.append(relative)
            else:
                missing.append(relative)
        if found and not missing:
            status = "source_implementation_evidence_found"
        elif found:
            status = "partial_source_implementation_evidence"
        else:
            status = "not_verified_by_targeted_source_audit"
        results[rule_id] = {
            "status": status,
            "evidence_files": found,
            "missing_expected_files": missing,
            "runtime_end_to_end_verified": False,
        }
    return {
        "development": "DEV-077S-I2-I-C3-D7-B4-B4-B",
        "scope": "profile_rules_only",
        "method": "targeted_source_identifier_presence",
        "limits": "Absence of evidence is not proof of absence; presence is not end-to-end validation.",
        "army_special_rules_included": False,
        "production_scoring_modified": False,
        "rules": results,
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
