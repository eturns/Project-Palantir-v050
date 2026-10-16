import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from loader import load_all_profiles
from army_loader import load_factions, load_army_lists
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from wargear_loader import load_wargear
from mount_loader import load_mounts
from analysis_loader import load_metric_thresholds
from scenario_analysis_context import (
    build_default_scenario_analysis_context,
)
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "tests" / "fixtures" / "iron_hills_army.json"
OUTPUT = ROOT / "docs" / "validation" / "dev073" / "iron_hills_baseline.json"

profiles = {profile.id: profile for profile in load_all_profiles()}
options = load_profile_options(profiles=profiles)

load_profile_option_wargear_assignments(options, load_wargear())
load_profile_option_mount_assignments(options, load_mounts())

result = analyse_mesbg_list_builder_file(
    str(FIXTURE),
    profiles_by_id=profiles,
    army_lists_by_id=load_army_lists(load_factions()),
    metric_thresholds=load_metric_thresholds(),
    profile_options_by_external_id=(
        build_profile_options_by_external_id(options)
    ),
)

from army_metric_densities import calculate_army_metric_densities
from battlefield_effects_input_builder import (
    build_battlefield_effects_inputs,
)

densities = calculate_army_metric_densities(
    result["army"],
    result["army_list"],
)

inputs = build_battlefield_effects_inputs(
    result["army"],
    result["army_list"],
)

print("Shooting density:", densities.shooting)
print("Magic density:", densities.magic)
print("Normalised shooting:", inputs.shooting)

definition = result["definition"]
army = result["army"]
scenarios = result["scenario_analysis_results"]

if result["analysis"]["validation_errors"]:
    raise RuntimeError(result["analysis"]["validation_errors"])

if scenarios is None or len(scenarios) != 24:
    raise RuntimeError("Expected exactly 24 scenario results.")

points_limit = (
    definition.points_limit
    if definition.points_limit is not None
    else army.total_points()
)
context = build_default_scenario_analysis_context(
    points_limit=points_limit
)

baseline = {
    "ticket": "DEV-073A",
    "commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip(),
    "fixture": str(FIXTURE.relative_to(ROOT)),
    "fixture_sha256": hashlib.sha256(
        FIXTURE.read_bytes()
    ).hexdigest(),
    "army": {
        "name": definition.name,
        "points": army.total_points(),
        "points_limit": points_limit,
        "models": army.model_count(),
    },
    "benchmarks": {
        "presence": context.benchmark_presence,
        "manoeuvrability": context.benchmark_manoeuvrability,
        "combat_capability": context.benchmark_combat_capability,
        "fate": context.benchmark_fate,
        "combat": {
            "fight": context.combat_benchmark.fight,
            "strength": context.combat_benchmark.strength,
            "defence": context.combat_benchmark.defence,
            "attacks": context.combat_benchmark.attacks,
            "wounds": context.combat_benchmark.wounds,
        },
    },
    "scenarios": [
        {
            "id": scenario.scenario_id,
            "name": scenario.scenario_name,
            "pool": scenario.pool.value,
            "score": scenario.score,
            "demands": [
                {
                    "dimension": demand.dimension.value,
                    "capability": demand.capability,
                    "intensity": demand.intensity,
                }
                for demand in scenario.demands
            ],
        }
        for scenario in scenarios
    ],
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(baseline, indent=2) + "\n",
    encoding="utf-8",
)

print(f"Baseline saved: {OUTPUT.relative_to(ROOT)}")
print(f"Points: {army.total_points()}")
print(f"Models: {army.model_count()}")
print(f"Scenarios: {len(scenarios)}")