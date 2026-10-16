"""DEV-077S-I2-I-C3-D3: run repository-backed mixed-points diagnostic rosters.

Run from repository root. Uses existing i2i_c3_real_army_evidence_run.py;
never changes scores, overwrites records, or approves calibration anchors.
"""
import argparse
import json
from pathlib import Path

from i2i_c3_real_army_evidence_run import run

ROOT = Path(__file__).resolve().parent

REFERENCE_CASES = (
    ("iron_hills", "tests/fixtures/iron_hills_army.json", 823, "Good"),
    ("garrison_of_dale", "tests/fixtures/garrison_of_dale.json", 177, "Good"),
    ("five_armies", "tests/fixtures/five_armies.json", 346, "Good"),
)


def validate_case(fixture, document, expected_points):
    if document.get("points") != expected_points:
        raise ValueError(f"Unexpected points for {fixture}: {document.get('points')} vs {expected_points}")
    if document.get("production_scoring_enabled") is not False:
        raise ValueError("Unexpected production scoring activation")
    if document.get("reference_anchors_approved") is not False:
        raise ValueError("Unexpected calibration anchor approval")
    if document.get("scenario_scoring_changed") is not False:
        raise ValueError("Unexpected scenario scoring change")
    if len(document.get("measurements", ())) != 10:
        raise ValueError("Expected ten measurement records")
    return True


def plan(out_dir):
    out_dir = Path(out_dir)
    return tuple((key, ROOT / fixture, out_dir / (key + "_evidence.json"), points, alignment)
                 for key, fixture, points, alignment in REFERENCE_CASES)


def execute(out_dir, *, runner=run):
    """Run all three verified filenames; require empty destinations up front."""
    jobs = plan(out_dir)
    missing = [str(fixture) for _, fixture, _, _, _ in jobs if not fixture.is_file()]
    if missing:
        raise FileNotFoundError("Missing roster fixtures: " + ", ".join(missing))
    existing = [str(output) for _, _, output, _, _ in jobs if output.exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite: " + ", ".join(existing))
    rows = []
    for key, fixture, output, expected_points, alignment in jobs:
        document = runner(str(fixture), str(output), key)
        validate_case(fixture, document, expected_points)
        rows.append({"army_key": key, "alignment": alignment,
                     "points": document["points"], "models": document["models"],
                     "commit": document["analysis_commit"],
                     "sha256": document["roster_sha256"],
                     "output": str(output),
                     "available": document["available_count"],
                     "partial": document["partial_count"],
                     "unresolved": document["unresolved_metrics"]})
    return tuple(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="docs/validation/i2i_c3")
    args = parser.parse_args(argv)
    rows = execute(ROOT / args.output_dir)
    print(json.dumps({"purpose": "mixed_points_diagnostic_only",
                      "anchors_approved": False, "production_scoring_enabled": False,
                      "armies": rows}, indent=2))
    print("IMPORTANT: Mixed points and Good-heavy reference population; not eligible as final 700-point benchmark anchors.")


if __name__ == "__main__":
    main()
