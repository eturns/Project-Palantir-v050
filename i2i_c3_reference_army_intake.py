"""DEV-077S-I2-I-C3-D6: qualify imported roster evidence for a 700-point cohort.

Research-only wrapper of the existing C3 engine. Accepts 695-700 points.
Does not change scores.
A candidate is NOT an approved calibration anchor.
"""
import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

from i2i_c3_real_army_evidence_run import run as run_evidence

ARCHETYPES = frozenset({"elite_magic", "infantry", "elite_infantry", "cavalry", "shooting", "mixed_arms", "hero_hunting", "monster"})
ALIGNMENTS = frozenset({"Good", "Evil"})
KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
MIN_REFERENCE_POINTS = 695
MAX_REFERENCE_POINTS = 700


def validate_intake_declaration(army_key, alignment, archetype, target_points=700):
    if not isinstance(army_key, str) or not KEY_PATTERN.fullmatch(army_key):
        raise ValueError("army_key must be a lowercase identifier of 3-64 characters")
    if alignment not in ALIGNMENTS:
        raise ValueError("alignment must be Good or Evil")
    if archetype not in ARCHETYPES:
        raise ValueError(f"archetype must be one of {', '.join(sorted(ARCHETYPES))}")
    if type(target_points) is not int or target_points != 700:
        raise ValueError("D7 research cohort target_points must be 700")


def assess_intake_evidence(document, *, army_key, alignment, archetype, target_points=700,
                           expected_sha256=None):
    """Return blockers; alignment and archetype remain user declarations.

    Never treats the uploader's alignment/archetype declaration as inferred
    from the faction roster. Independent faction mapping review is required.
    """
    validate_intake_declaration(army_key, alignment, archetype, target_points)
    if not isinstance(document, dict):
        raise TypeError("evidence document must be a mapping")
    blockers = []
    if document.get("source") != "fresh_real_army_engine_run":
        blockers.append("not_fresh_engine_evidence")
    if document.get("army_key") != army_key:
        blockers.append("army_key_mismatch")
    measured_points = document.get("points")
    if type(measured_points) is not int or not (target_points - 5 <= measured_points <= target_points):
        blockers.append("outside_reference_points_range")
    if not isinstance(document.get("models"), int) or document["models"] <= 0:
        blockers.append("no_fielded_models")
    digest = document.get("roster_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
        blockers.append("missing_valid_roster_hash")
    if expected_sha256 is not None and digest != expected_sha256:
        blockers.append("roster_hash_mismatch")
    if not isinstance(document.get("analysis_commit"), str) or not document["analysis_commit"].strip():
        blockers.append("missing_engine_commit")
    if not isinstance(document.get("measurements"), list) or len(document["measurements"]) != 10:
        blockers.append("missing_ten_metric_evidence")
    if document.get("production_scoring_enabled") is not False or document.get("reference_anchors_approved") is not False or document.get("scenario_scoring_changed") is not False:
        blockers.append("unexpected_scoring_activation")
    return {
        "army_key": army_key,
        "declared_alignment": alignment,
        "declared_archetype": archetype,
        "alignment_and_archetype_verified": False,
        "target_points": target_points,
        "min_reference_points": target_points - 5,
        "max_reference_points": target_points,
        "measured_points": document.get("points"),
        "roster_sha256": digest,
        "analysis_commit": document.get("analysis_commit"),
        "points_and_evidence_qualified": not blockers,
        "calibration_eligible": False,
        "blockers": blockers,
        "review_required": ["independent_faction_alignment_check", "archetype_classification_check", "cohort_population_quality_gate"],
        "anchors_approved": False,
        "production_scoring_enabled": False,
    }


def intake_roster(*, fixture, output, army_key, alignment, archetype, target_points=700):
    """Run production importer to temporary evidence; persist only if qualified.

    Refuses to overwrite; output is a new standalone evidence JSON.
    """
    validate_intake_declaration(army_key, alignment, archetype, target_points)
    fixture = Path(fixture).resolve()
    output = Path(output).resolve()
    if not fixture.is_file() or fixture.suffix.lower() != ".json":
        raise ValueError("fixture must be an existing JSON roster")
    if output.exists() or fixture == output:
        raise ValueError("refusing to overwrite existing output or roster")
    source_hash = hashlib.sha256(fixture.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="palantir-i2i-intake-") as temp:
        temporary_output = Path(temp) / "raw_evidence.json"
        document = run_evidence(fixture, temporary_output, army_key)
    verdict = assess_intake_evidence(document, army_key=army_key, alignment=alignment,
                                     archetype=archetype, target_points=target_points,
                                     expected_sha256=source_hash)
    if verdict["blockers"]:
        return verdict
    document["reference_intake"] = verdict
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(document, handle, indent=2)
        handle.write("\n")
    return verdict


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--army-key", required=True)
    parser.add_argument("--alignment", required=True, choices=sorted(ALIGNMENTS))
    parser.add_argument("--archetype", required=True, choices=sorted(ARCHETYPES))
    parser.add_argument("--target-points", type=int, default=700)
    args = parser.parse_args(argv)
    verdict = intake_roster(fixture=args.fixture, output=args.output,
                            army_key=args.army_key, alignment=args.alignment,
                            archetype=args.archetype, target_points=args.target_points)
    print(json.dumps(verdict, indent=2))
    if verdict["blockers"]:
        raise SystemExit("Roster not qualified: evidence not saved")
    print("Evidence saved; alignment/archetype review and cohort gate still required.")


if __name__ == "__main__":
    main()
