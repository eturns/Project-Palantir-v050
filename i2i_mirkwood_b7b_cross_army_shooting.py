"""DEV-077S-I2-I-C3-D7-B7-B: read-only cross-army shooting diagnostics.

Compare only actual supplied roster files. No fictional armies, automatic
roster substitutions, calibrated scores, or silent import failures.
Usage:
  py -3.14 i2i_mirkwood_b7b_cross_army_shooting.py
  py -3.14 i2i_mirkwood_b7b_cross_army_shooting.py --army KEY=path/to/list.json
"""
import argparse
import json
from pathlib import Path
from fractions import Fraction

from i2i_mirkwood_b5_shooting_evidence import load_reference_army
from i2i_mirkwood_b6_shooting_benchmarks import (
    benchmark_defender,
    DEFENCES,
)
from army_shooting_capability import resolve_army_ranged_shooters
from shooting_eligibility import ShootingContext, can_shoot
from shooting_to_hit_modifier import get_movement_shooting_modifier
from shooting_attack_count import get_effective_shooting_attack_count
from shooting_wound_probability import get_expected_shooting_wounds

DEFAULT_INPUTS = {
    "rangers_of_mirkwood_700": "tests/fixtures/rangers-of-mirkwood.json",
    "azogs_hunters": "tests/fixtures/azogs-hunters.json",
}


def evaluate_army(army, *, label: str) -> dict:
    points = army.total_points()
    models = tuple(army.fielded_models())
    if not models or points <= 0:
        raise ValueError("Army must have models and positive points")
    shooters = resolve_army_ranged_shooters(army)
    if any(not w.is_mechanically_complete for _, w in shooters):
        raise ValueError("Incomplete ranged weapon mechanics")
    benchmark_rows = []
    for defence in DEFENCES:
        defender = benchmark_defender(defence)
        for moved in (False, True):
            ctx = ShootingContext(moved_this_turn=moved, target_distance_inches=12)
            wounds = Fraction(0, 1)
            attacks = 0
            eligible = 0
            for shooter, weapon in shooters:
                if not can_shoot(shooter=shooter, weapon=weapon, context=ctx):
                    continue
                eligible += 1
                attacks += weapon.shots * get_effective_shooting_attack_count(shooter)
                wounds += get_expected_shooting_wounds(
                    attacker=shooter, defender=defender, weapon=weapon,
                    to_hit_modifier=get_movement_shooting_modifier(
                        shooter, moved_this_turn=moved),
                )
            benchmark_rows.append({
                "defence": defence, "moved": moved,
                "eligible_shooters": eligible, "normal_attacks": attacks,
                "expected_wounds": float(wounds),
                "expected_wounds_per_100_points": float(wounds * 100 / points),
            })
    return {
        "army": label, "points": points, "models": len(models),
        "armed_shooters": len(shooters), "benchmarks": benchmark_rows,
        "reference_points_eligible": 695 <= points <= 700,
    }


def compare(inputs: dict[str, str]) -> dict:
    results = []
    blockers = []
    for key, raw_path in sorted(inputs.items()):
        path = Path(raw_path)
        if not path.is_file():
            blockers.append({"army": key, "status": "missing_fixture", "path": str(path)})
            continue
        try:
            army = load_reference_army(path)
            results.append(evaluate_army(army, label=key))
        except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
            blockers.append({"army": key, "status": "evaluation_failed",
                             "reason": f"{type(exc).__name__}: {exc}"})
    return {
        "stage": "B7-B", "scope": "read_only_cross_army_shooting",
        "assumptions": "12-inch unobstructed line of sight; full eligible target availability; stationary/moving; D3/D5/D7; no tactical bonuses or Pinpoint",
        "armies": results, "blockers": blockers,
        "comparison_available": len(results) >= 2,
        "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--army", action="append", default=[],
                        help="Army key and JSON path: KEY=path.json")
    args = parser.parse_args()
    inputs = dict(DEFAULT_INPUTS) if not args.army else {}
    for item in args.army:
        key, separator, path = item.partition("=")
        if not separator or not key.strip() or not path.strip():
            parser.error("--army entries must be KEY=path.json")
        inputs[key.strip()] = path.strip()
    print(json.dumps(compare(inputs), indent=2))


if __name__ == "__main__":
    main()
