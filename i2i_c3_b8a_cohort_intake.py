"""B8-A: six-army fixture and production-import qualification (read only).

Runs from the project root. Candidate admission is not calibration approval.
Uses the existing B5 production loader; reports import errors without hiding them.
"""
import json
from pathlib import Path
from i2i_mirkwood_b5_shooting_evidence import load_reference_army

FIXTURES = {
    "dol_guldur": ("dol_guldur_700.json", "Evil", "elite_magic"),
    "azogs_hunters": ("azogs-hunters.json", "Evil", "mobile_assault"),
    "pits_of_dol_guldur": ("pits-of-dol-guldur.json", "Evil", "mixed_infantry_assault"),
    "rangers_of_mirkwood": ("rangers-of-mirkwood.json", "Good", "mass_shooting"),
    "five_armies": ("five_armies_cal.json", "Good", "combined_arms"),
    "iron_hills": ("iron-hills-cal.json", "Good", "armoured_defence"),
}
FIXTURE_DIR = Path("tests/fixtures")


def inspect_fixture(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    warbands = data.get("warbands")
    if not isinstance(warbands, list) or not warbands:
        raise ValueError("Missing or empty warbands")
    declared_points = 0
    model_count = 0
    options = []
    models = {}
    for index, band in enumerate(warbands, 1):
        hero = band.get("hero")
        if not isinstance(hero, dict) or not hero.get("model_id"):
            raise ValueError(f"Missing hero in warband {index}")
        for model_id, n in [(hero["model_id"], 1)] + [
            (unit["model_id"], unit["quantity"]) for unit in band.get("units", [])
        ]:
            if type(n) is not int or n < 1:
                raise ValueError(f"Invalid unit quantity in warband {index}")
            models[model_id] = models.get(model_id, 0) + n
            model_count += n
        points = band.get("meta", {}).get("points")
        if type(points) is not int:
            raise ValueError(f"Missing warband point declaration in warband {index}")
        declared_points += points
        for model in [hero] + band.get("units", []):
            for opt in model.get("options", []):
                options.append({
                    "model_id": model["model_id"],
                    "option_id": opt.get("id"),
                    "name": opt.get("name"),
                    "model_quantity": model.get("quantity", 1),
                })
    return {
        "declared_points": declared_points,
        "points_window_passed": 695 <= declared_points <= 700,
        "models": model_count, "warbands": len(warbands),
        "option_assignments": options,
        "model_counts": models,
        "army_list": data.get("armyList"),
        "edition": data.get("edition"),
        "declared_limit": data.get("metadata", {}).get("maxPoints"),
    }


def audit_one(key: str, filename: str, alignment: str, archetype: str,
              root: Path = FIXTURE_DIR, importer=load_reference_army) -> dict:
    path = root / filename
    report = {
        "key": key, "file": str(path), "alignment": alignment,
        "proposed_archetype": archetype, "archetype_review_approved": False,
        "status": "blocked", "issues": [],
    }
    if not path.is_file():
        report["issues"].append("fixture_missing")
        return report
    try:
        declared = inspect_fixture(path)
        report.update(declared)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        report["issues"].append(f"invalid_fixture: {type(exc).__name__}: {exc}")
        return report
    if not declared["points_window_passed"]:
        report["issues"].append("points_outside_695_700")
    try:
        army = importer(path)
        report["imported_points"] = army.total_points()
        report["imported_models"] = len(tuple(army.fielded_models()))
        if report["imported_points"] != declared["declared_points"]:
            report["issues"].append("imported_points_mismatch")
        if report["imported_models"] != declared["models"]:
            report["issues"].append("imported_models_mismatch")
    except Exception as exc:
        report["issues"].append(f"production_import_failed: {type(exc).__name__}: {exc}")
    report["status"] = "intake_passed" if not report["issues"] else "blocked"
    return report


def audit_cohort(root: Path = FIXTURE_DIR, importer=load_reference_army) -> dict:
    rows = [
        audit_one(key, filename, alignment, archetype, root, importer)
        for key, (filename, alignment, archetype) in FIXTURES.items()
    ]
    intake_passed = [r for r in rows if r["status"] == "intake_passed"]
    aligned = {side: sum(r["alignment"] == side for r in intake_passed)
               for side in ("Good", "Evil")}
    gate = (len(intake_passed) >= 6 and aligned["Good"] >= 3
            and aligned["Evil"] >= 3
            and len(set(r["proposed_archetype"] for r in intake_passed)) >= 4)
    return {
        "stage": "B8-A", "status": "intake_gate_passed" if gate else "intake_gate_blocked",
        "intake_passed": len(intake_passed), "candidates": len(rows),
        "intake_alignment_counts": aligned, "results": rows,
        "independent_archetype_review_pending": True,
        "full_mechanical_qualification_pending": True,
        "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit_cohort(), indent=2))
