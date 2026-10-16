"""B6: read-only Mirkwood shooting benchmarks against D3/D5/D7.

All shots assumed in range, with clear line of sight, no In The Way rolls,
no cover and no casualties. One complete shooting phase is modelled.
Does not infer a calibrated Shooting score or change production files.
"""
from collections import Counter
from fractions import Fraction
import json

from configured_profile import ConfiguredProfile
from profiles import Profile
from army_shooting_capability import resolve_army_ranged_shooters
from shooting_eligibility import ShootingContext, can_shoot
from shooting_to_hit_modifier import get_movement_shooting_modifier
from shooting_wound_probability import get_expected_shooting_wounds
from shooting_attack_count import get_effective_shooting_attack_count
from i2i_mirkwood_b5_shooting_evidence import load_reference_army

DEFENCES = (3, 5, 7)
ARMY_POINTS = 700
MODELS = 33


def benchmark_defender(defence: int) -> ConfiguredProfile:
    if defence not in DEFENCES:
        raise ValueError("Unsupported benchmark Defence")
    return ConfiguredProfile(profile=Profile(
        id=f"B6_DEFENCE_{defence}", name=f"Benchmark Defence {defence}",
        points=0, movement=6, fight=3, shooting="4+", strength=3,
        defence=defence, attacks=1, wounds=1, courage="6+",
        intelligence="6+", might=0, will=0, fate=0, max_in_army=0,
    ))


def scenario(shooters, *, defence: int, moved: bool) -> dict:
    defender = benchmark_defender(defence)
    context = ShootingContext(moved_this_turn=moved, target_distance_inches=12)
    wounds = Fraction(0, 1)
    attacks = 0
    eligible_models = 0
    by_profile = Counter()
    for shooter, weapon in shooters:
        if not weapon.is_mechanically_complete:
            raise ValueError("Mechanically incomplete ranged weapon")
        if not can_shoot(shooter=shooter, weapon=weapon, context=context):
            continue
        shots = weapon.shots * get_effective_shooting_attack_count(shooter)
        attacks += shots
        eligible_models += 1
        modifier = get_movement_shooting_modifier(
            shooter, moved_this_turn=moved
        )
        expected = get_expected_shooting_wounds(
            attacker=shooter, defender=defender, weapon=weapon,
            to_hit_modifier=modifier,
        )
        wounds += expected
        by_profile[shooter.profile.id] += expected
    return {
        "defence": defence, "moved": moved,
        "eligible_models": eligible_models, "normal_attacks": attacks,
        "expected_wounds": float(wounds),
        "expected_wounds_fraction": str(wounds),
        "expected_wounds_per_100_points": float(wounds * 100 / ARMY_POINTS),
        "by_profile": {k: float(v) for k,v in sorted(by_profile.items())},
    }


def measure() -> dict:
    army = load_reference_army()
    if army.total_points() != ARMY_POINTS or army.model_count() != MODELS:
        raise ValueError("Reference army is not the qualified 700pt/33-model roster")
    shooters = resolve_army_ranged_shooters(army)
    if len(shooters) != MODELS:
        raise ValueError("Not all 33 models have resolved ranged weapons")
    results = [
        scenario(shooters, defence=defence, moved=moved)
        for defence in DEFENCES for moved in (False, True)
    ]
    return {
        "stage": "B6", "army": "RANGERS_OF_MIRKWOOD",
        "points": ARMY_POINTS, "models": MODELS,
        "assumptions": [
            "All 33 models shoot at an eligible visible target within 12 inches",
            "No intervening models, cover or In The Way rolls",
            "No Might spending, heroics, casualties or Pinpoint alternative",
            "Stationary/moved scenarios use the current production movement To Hit resolver",
            "These are expected wounds per shooting phase, not kills or a score",
        ],
        "benchmarks": results, "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }


if __name__ == "__main__":
    print(json.dumps(measure(), indent=2))
