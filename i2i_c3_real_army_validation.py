"""DEV-077S-I2-I-C3-D7-B: real-roster intake with shooting safeguards.

Run from repository root. Imports actual armies using the D6 engine pathway.
Does not declare roster legality from export metadata alone.
"""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from i2i_c3_reference_army_intake import intake_roster

ROSTERS = {
    "azogs_hunters_700": ("azogs-hunters.json", "Evil", "cavalry"),
    "rangers_of_mirkwood_700": ("rangers-of-mirkwood.json", "Good", "shooting"),
}
MIN_POINTS, MAX_POINTS = 695, 700


def inspect_export(path):
    """Only inspect declarative export metadata; never infer equipped bows."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    warbands = data.get("warbands")
    if not isinstance(warbands, list) or not warbands:
        raise ValueError("Expected nonempty MESBG List Builder warbands")
    total = 0
    models = 0
    for wb in warbands:
        meta = wb.get("meta", {})
        points = meta.get("points")
        if type(points) is not int or points < 0:
            raise ValueError("Export warband points missing")
        total += points
        models += 1 + sum(u["quantity"] for u in wb.get("units", []))
    return {
        "export_points": total,
        "export_models": models,
        "export_bow_limit_count": sum(wb.get("meta", {}).get("bows", 0) for wb in warbands),
        "army_list": data.get("armyList"),
        "edition": data.get("edition"),
    }


def review_evidence(document, *, army_key, export):
    """Block qualification on genuine shooting failures, never bow-limit counts."""
    blockers = []
    actual = document.get("points")
    if type(actual) is not int or not MIN_POINTS <= actual <= MAX_POINTS:
        blockers.append("engine_points_outside_695_700")
    if actual != export["export_points"]:
        blockers.append("engine_export_points_mismatch")
    if document.get("models") != export["export_models"]:
        blockers.append("engine_export_model_count_mismatch")
    values = {m.get("metric"): m for m in document.get("measurements", [])}
    shooting = values.get("shooting", {})
    if army_key == "rangers_of_mirkwood_700":
        if shooting.get("availability") != "available" or not isinstance(
            shooting.get("value"), (float, int)
        ) or isinstance(shooting.get("value"), bool) or shooting["value"] <= 0:
            blockers.append("rangers_default_bow_shooting_not_resolved")
    return tuple(blockers)


def validate_roster(*, fixture, output, army_key, alignment, archetype):
    fixture, output = Path(fixture).resolve(), Path(output).resolve()
    if not fixture.is_file():
        raise FileNotFoundError(fixture)
    if output.exists() or fixture == output:
        raise ValueError("Refusing to overwrite output/fixture")
    export = inspect_export(fixture)
    with tempfile.TemporaryDirectory(prefix="i2i-d7b-") as d:
        temp_output = Path(d) / "validated.json"
        verdict = intake_roster(
            fixture=fixture, output=temp_output, army_key=army_key,
            alignment=alignment, archetype=archetype,
        )
        blockers = list(verdict["blockers"])
        if not blockers:
            document = json.loads(temp_output.read_text(encoding="utf-8"))
            blockers.extend(review_evidence(document, army_key=army_key, export=export))
        result = dict(verdict)
        result["export"] = export
        result["blockers"] = blockers
        result["points_and_evidence_qualified"] = not blockers
        result["calibration_eligible"] = False
        result["anchors_approved"] = False
        if not blockers:
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8") as f:
                f.write(temp_output.read_text(encoding="utf-8"))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster-dir", default="tests/fixtures")
    parser.add_argument("--output-dir", default="docs/validation/i2i_c3")
    args = parser.parse_args(argv)
    results = []
    for key, (filename, alignment, archetype) in ROSTERS.items():
        try:
            result = validate_roster(
                fixture=Path(args.roster_dir)/filename,
                output=Path(args.output_dir)/(key+"_evidence.json"),
                army_key=key, alignment=alignment, archetype=archetype,
            )
        except (ValueError, FileNotFoundError, RuntimeError, KeyError) as exc:
            result = {"army_key": key, "points_and_evidence_qualified": False,
                      "blockers": [f"import_or_validation_error:{type(exc).__name__}:{exc}"]}
        results.append(result)
    print(json.dumps({"stage": "D7-B", "results": results,
                      "anchors_approved": False,
                      "production_scoring_enabled": False}, indent=2))
    if any(not r["points_and_evidence_qualified"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
