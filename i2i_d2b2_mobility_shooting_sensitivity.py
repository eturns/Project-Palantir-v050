"""DEV-077S-I2-I-D2-B2: read-only terrain and shooting sensitivity.

No calibration approvals, production scoring or army-list changes.
Terrain values are accessibility indices, not inches or scenario scores.
Shooting assumes the same stationary D6 benchmark defender used in D1.
"""
import json
from pathlib import Path

from army_shooting_capability import (
    calculate_shooting_output_density,
    get_army_expected_shooting_wounds,
    resolve_army_ranged_shooters,
)
from i2i_c3_b8a_cohort_intake import FIXTURES, FIXTURE_DIR
from i2i_c3_b8b_mechanical_qualification import load_reference_army_with_platforms
from i2i_c3_b8c_reference_qualification import read_json
from i2i_d1_exploratory_measurement_matrix import benchmark_target
from mobility_integration_contract import build_mobility_integration_contract
from shooting_eligibility import ShootingContext

ROOT = Path(__file__).resolve().parent
QUALIFICATION = ROOT / "b8c_reference_qualification.json"
D1 = ROOT / "i2i_d1_measurement_matrix.json"
CONDITIONS = ("stationary", "moved_this_turn")
SHOOTING_TARGET = "common_D6_benchmark"

def gate_ok(evidence):
    if not isinstance(evidence, dict):
        return False
    armies = evidence.get("armies")
    if not isinstance(armies, list):
        return False
    qualified = {
        r.get("army") for r in armies if isinstance(r, dict)
        and r.get("candidate_status") == "provisional_reference"
        and not r.get("candidate_issues")
    }
    return (
        evidence.get("stage") == "B8-C"
        and evidence.get("status") == "provisional_evidence_qualified"
        and evidence.get("qualification_errors") == []
        and evidence.get("provisional_references") == 6
        and len(armies) == 6
        and qualified == set(FIXTURES)
        and evidence.get("calibration_anchors_approved") is False
        and evidence.get("numerical_calibration_permitted") is False
    )

def shoot_density(army, defender, *, moved):
    shooters = resolve_army_ranged_shooters(army)
    # Never reinterpret incomplete weapons as zero firepower.
    if any(not weapon.is_mechanically_complete for _, weapon in shooters):
        raise ValueError("Incomplete ranged weapon mechanics")
    state = ShootingContext(moved_this_turn=moved)
    entries = tuple((profile, weapon, state) for profile, weapon in shooters)
    wounds = get_army_expected_shooting_wounds(
        shooters=entries, defender=defender
    )
    return float(calculate_shooting_output_density(
        expected_wounds=wounds, army_points=army.total_points()
    )), len(shooters)

def measure_army(army, defender):
    m = build_mobility_integration_contract(army)
    stationary, ranged = shoot_density(army, defender, moved=False)
    moving, moving_ranged = shoot_density(army, defender, moved=True)
    return {
        "army_points": army.total_points(),
        "model_count": army.model_count(),
        "ranged_model_count": ranged,
        "mobility": {
            "open_ground": float(m.open_ground.value),
            "difficult_terrain": float(m.difficult_terrain.value),
            "terrain_retention": float(m.terrain_retention.value),
        },
        "shooting": {
            "stationary": stationary,
            "moved_this_turn": moving,
            "retention_when_moving": (
                moving / stationary if stationary > 0 else None
            ),
        },
        "notes": {
            "zero_shooting": (
                "no mechanically resolved shooters" if ranged == 0 else None
            ),
            "movement_not_scenario_coverage": True,
            "range_and_target_access": (
                "hypothetical target in range; no in-the-way tests"
            ),
        }
    }

def descending_rank(rows, metric, variant):
    scored = [
        (r["army"], r["measurements"][metric][variant])
        for r in rows if "measurements" in r
    ]
    return [army for army, _ in sorted(scored, key=lambda item: (-item[1], item[0]))]

def build_report(evidence, *, importer=load_reference_army_with_platforms):
    if not gate_ok(evidence):
        return {"stage": "I2-I-D2-B2", "status": "blocked_by_qualification_gate",
                "rows": [], "production_scoring_modified": False,
                "numerical_calibration_permitted": False}
    defender = benchmark_target()
    rows = []
    for key, (filename, alignment, archetype) in FIXTURES.items():
        try:
            army = importer(FIXTURE_DIR / filename)
            value = measure_army(army, defender)
            rows.append({"army": key, "alignment": alignment,
                         "proposed_archetype": archetype, "measurements": value})
        except Exception as exc:
            rows.append({"army": key,
                         "error": type(exc).__name__ + ": " + str(exc)})
    errors = [r for r in rows if "error" in r]
    ranking = {}
    if not errors:
        for metric, variants in {
            "mobility": ("open_ground", "difficult_terrain", "terrain_retention"),
            "shooting": ("stationary", "moved_this_turn"),
        }.items():
            ranking[metric] = {
                v: descending_rank(rows, metric, v)
                for v in variants
            }
    return {
        "stage": "I2-I-D2-B2",
        "status": "sensitivity_complete" if not errors else "incomplete",
        "reference_armies": len(FIXTURES),
        "rows": rows, "rankings": ranking,
        "errors": errors,
        "benchmark": {
            "shooting_defender": SHOOTING_TARGET,
            "movement_conditions": ["open_ground", "difficult_terrain"],
            "shooting_conditions": list(CONDITIONS),
        },
        "limitations": [
            "Read-only diagnostics, not scenario outcomes or calibrated scores.",
            "Difficult terrain uses the current mechanical terrain resolver.",
            "In-the-way, targeting, battlefield position and ammunition not simulated.",
            "Moving-fire assumes every resolved shooter attempts to shoot.",
            "Platform physical mechanics and rulebook completeness unapproved.",
            "No automatic treatment of missing mechanics as zero."
        ],
        "calibration_anchors_approved": False,
        "numerical_calibration_permitted": False,
        "production_scoring_modified": False,
    }

if __name__ == "__main__":
    if not QUALIFICATION.exists():
        print(json.dumps({"stage": "I2-I-D2-B2",
                          "status": "missing_qualification_file"}, indent=2))
        raise SystemExit(2)
    print(json.dumps(build_report(read_json(QUALIFICATION)), indent=2))
