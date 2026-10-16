"""DEV-077S-I2-I-C3-D7-B3: evidence-backed Azog's Hunters reference review.

Read-only. Does not validate army legality, change scoring or approve anchors.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_LIST = "Azog's Hunters"
EXPECTED_ARMY_KEY = "azogs_hunters_700"
EXPECTED_PREFIX = "[azog's-hunters] "
HUNTER_WARG_RIDER = EXPECTED_PREFIX + "hunter-orc-warg-rider"
FELL_WARG = EXPECTED_PREFIX + "fell-warg"
MOUNT_OPTION_IDS = frozenset({"OPT0690", "OPT0691"})


def review(roster: dict, evidence: dict, *, roster_sha256: str) -> dict:
    """Compare an imported evidence record with the original unchanged export."""
    if not isinstance(roster, dict) or not isinstance(evidence, dict):
        raise TypeError("roster and evidence must be mappings")
    if not isinstance(roster_sha256, str) or len(roster_sha256) != 64:
        raise ValueError("full roster SHA-256 is required")
    blockers = []
    if roster.get("edition") != "v2024" or roster.get("armyList") != EXPECTED_LIST:
        blockers.append("wrong_edition_or_army_list")
    if evidence.get("army_key") != EXPECTED_ARMY_KEY:
        blockers.append("wrong_evidence_army_key")
    if evidence.get("roster_sha256") != roster_sha256:
        blockers.append("roster_content_hash_mismatch")
    if evidence.get("source") != "fresh_real_army_engine_run":
        blockers.append("not_a_fresh_engine_run")
    if not isinstance(evidence.get("analysis_commit"), str) or not evidence["analysis_commit"].strip():
        blockers.append("missing_analysis_commit")
    if any(evidence.get(k) is not False for k in (
        "reference_anchors_approved", "production_scoring_enabled", "scenario_scoring_changed"
    )):
        blockers.append("scoring_isolation_not_confirmed")
    warbands = roster.get("warbands", [])
    if not isinstance(warbands, list) or not warbands:
        raise ValueError("roster has no warbands")
    points = 0
    models = 0
    rider_count = 0
    warg_count = 0
    mounted_hero_options = 0
    for wb in warbands:
        points += wb["meta"]["points"]
        hero = wb.get("hero")
        if hero:
            models += 1
            hero_options = {o["id"] for o in hero.get("options", [])}
            if hero_options & MOUNT_OPTION_IDS:
                mounted_hero_options += 1
        for unit in wb.get("units", []):
            qty = unit["quantity"]
            models += qty
            if unit["model_id"] == HUNTER_WARG_RIDER:
                rider_count += qty
            if unit["model_id"] == FELL_WARG:
                warg_count += qty
    if not (695 <= points <= 700) or evidence.get("points") != points:
        blockers.append("reference_points_mismatch")
    if evidence.get("models") != models:
        blockers.append("model_count_mismatch")
    if not (rider_count > 0 and warg_count > 0 and mounted_hero_options > 0):
        blockers.append("insufficient_roster_evidence_for_mobile_archetype")
    measurements = evidence.get("measurements", [])
    if not isinstance(measurements, list) or len(measurements) != 10:
        blockers.append("missing_ten_measurements")
    identity_passed = not blockers
    return {
        "development": "DEV-077S-I2-I-C3-D7-B3",
        "army_key": EXPECTED_ARMY_KEY,
        "roster_faction": EXPECTED_LIST,
        "alignment": "Evil" if roster.get("armyList") == EXPECTED_LIST else None,
        "alignment_basis": "explicit_faction_reference_mapping_Azogs_Hunters_Evil",
        "reference_archetype": "mobile_mixed_assault" if not ("insufficient_roster_evidence_for_mobile_archetype" in blockers) else None,
        "archetype_basis": "roster_mounted_options_warg_riders_and_fell_wargs_not_pure_cavalry",
        "mount_option_heroes": mounted_hero_options,
        "warg_riders": rider_count,
        "fell_wargs": warg_count,
        "export_points": points,
        "export_models": models,
        "evidence_identity_and_composition_verified": identity_passed,
        "army_list_rules_legality_verified": False,
        "calibration_eligible": False,
        "anchors_approved": False,
        "production_scoring_enabled": False,
        "blockers": blockers,
        "review_required": ["army_list_rules_legality_review", "cohort_population_quality_gate"],
    }


def run(roster_path, evidence_path, output_path):
    roster_path, evidence_path, output_path = map(Path, (roster_path, evidence_path, output_path))
    if output_path.exists() or output_path.resolve() in (roster_path.resolve(), evidence_path.resolve()):
        raise ValueError("Refusing to overwrite evidence, roster or existing review")
    data = roster_path.read_bytes()
    report = review(json.loads(data), json.loads(evidence_path.read_text(encoding="utf-8")),
                    roster_sha256=hashlib.sha256(data).hexdigest())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", default="tests/fixtures/azogs-hunters.json")
    parser.add_argument("--evidence", default="docs/validation/i2i_c3/azogs_hunters_700_evidence.json")
    parser.add_argument("--output", default="docs/validation/i2i_c3/azogs_hunters_reference_review.json")
    args = parser.parse_args()
    result = run(args.roster, args.evidence, args.output)
    print(json.dumps(result, indent=2))
    if result["blockers"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
