"""Read-only DEV-077S-I2-H score preservation verification.

Runs the existing DEV-073F validation script against its original fixtures,
storing temporary outputs outside the repository. Compares 96 scenario scores
and constituent demands against the revised DEV-073F reference snapshots.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / "docs" / "validation" / "dev073"
RUNNER = ROOT / "run_dev073f_validation.py"
ARMIES = {
    "Five Armies": "dev073f_five_armies_validation.json",
    "Garrison of Dale": "dev073f_garrison_of_dale_validation.json",
    "Iron Hills": "dev073f_iron_hills_validation.json",
    "Dol Guldur": "dev073f_dol_guldur_700_validation.json",
}
TOLERANCE = 1e-10


def numeric_match(a: object, b: object) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return False
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= TOLERANCE


def compare(reference: dict, current: dict, name: str) -> list[str]:
    issues: list[str] = []
    for field in ("fixture_sha256",):
        if reference.get(field) != current.get(field):
            issues.append(f"{name}: {field} mismatch")
    for field in ("points", "points_limit", "models"):
        if reference.get("army", {}).get(field) != current.get("army", {}).get(field):
            issues.append(f"{name}: army.{field} mismatch")
    if reference.get("benchmarks") != current.get("benchmarks"):
        issues.append(f"{name}: benchmark configuration changed")

    old_scenarios = {s["id"]: s for s in reference["scenarios"]}
    new_scenarios = {s["id"]: s for s in current["scenarios"]}
    if len(reference["scenarios"]) != 24 or len(current["scenarios"]) != 24:
        issues.append(f"{name}: expected exactly 24 scenarios in each set")
    if set(old_scenarios) != set(new_scenarios):
        issues.append(f"{name}: scenario ID set changed")
    for scenario_id in sorted(set(old_scenarios) & set(new_scenarios)):
        old, new = old_scenarios[scenario_id], new_scenarios[scenario_id]
        prefix = f"{name} / {scenario_id}"
        if old.get("pool") != new.get("pool"):
            issues.append(f"{prefix}: scenario pool changed")
        if not numeric_match(old["score"], new["score"]):
            issues.append(f"{prefix}: score {old['score']:.12g} -> {new['score']:.12g}")
        old_demands = {d["dimension"]: d for d in old["demands"]}
        new_demands = {d["dimension"]: d for d in new["demands"]}
        if set(old_demands) != set(new_demands):
            issues.append(f"{prefix}: demand dimensions changed")
        for dimension in sorted(set(old_demands) & set(new_demands)):
            for field in ("capability", "intensity"):
                old_value = old_demands[dimension][field]
                new_value = new_demands[dimension][field]
                if not numeric_match(old_value, new_value):
                    issues.append(
                        f"{prefix} / {dimension}: {field} "
                        f"{old_value:.12g} -> {new_value:.12g}"
                    )
    return issues


def main() -> int:
    if not RUNNER.is_file():
        print(f"Missing runner: {RUNNER}", file=sys.stderr)
        return 2
    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix="palantir_i2h_verify_") as temp:
        for name, snapshot in ARMIES.items():
            source = REFERENCE / snapshot
            if not source.is_file():
                problems.append(f"{name}: missing historical snapshot {source}")
                continue
            historical = json.loads(source.read_text(encoding="utf-8"))
            fixture = ROOT / historical["fixture"]
            if not fixture.is_file():
                problems.append(f"{name}: missing fixture {fixture}")
                continue
            output = Path(temp) / snapshot
            # The runner resolves absolute paths correctly via Path.__truediv__.
            result = subprocess.run(
                [sys.executable, str(RUNNER), str(fixture), str(output)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            # The legacy runner writes the JSON before its final status print.
            # When OUTPUT is outside ROOT, that print calls relative_to(ROOT)
            # and raises ValueError. Accept ONLY this exact post-write failure.
            post_write_print_error = (
                result.returncode != 0
                and output.is_file()
                and 'print(f"Baseline saved: {OUTPUT.relative_to(ROOT)}")' in result.stderr
                and 'ValueError:' in result.stderr
                and 'is not in the subpath of' in result.stderr
            )
            if result.returncode != 0 and not post_write_print_error:
                problems.append(
                    f"{name}: current analysis failed (exit {result.returncode})\n"
                    f"{(result.stdout + result.stderr)[-2500:]}"
                )
                continue
            if post_write_print_error:
                print(f"{name}: ignored known post-write filename-display error")
            if not output.is_file():
                problems.append(f"{name}: runner did not produce temporary output")
                continue
            current = json.loads(output.read_text(encoding="utf-8"))
            issues = compare(historical, current, name)
            print(f"{name}: {len(current['scenarios'])} scenarios; "
                  f"{'PASS' if not issues else f'{len(issues)} DIFFERENCES'}")
            problems.extend(issues)

    print("\nReference: DEV-073F revised snapshots | tolerance: 1e-10")
    print("Historical files were not modified. Temporary outputs deleted.")
    if problems:
        print(f"\nFAILED: {len(problems)} differences or errors")
        for problem in problems[:40]:
            print(" -", problem)
        if len(problems) > 40:
            print(f" ... and {len(problems) - 40} more")
        return 1
    print("PASS: 4 armies, 96 scenarios; scenario scores and demands unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
