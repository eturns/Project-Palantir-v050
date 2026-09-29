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

from rule_loader import (
    load_special_rules,
    load_heroic_actions,
    load_spells,
    load_ability_tags,
    load_ability_prerequisites,
)

from relationship_loader import (
    load_profile_special_rules,
    load_profile_heroic_actions,
    load_profile_spells,
    load_heroic_action_tags,
    load_special_rule_tags,
    load_spell_tags,
    load_heroic_action_prerequisites,
    load_special_rule_prerequisites,
    load_spell_prerequisites,
)

from profile_option_platform_loader import (
    load_profile_option_platform_assignments,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)
from model_platform_loader import load_platforms

ROOT = Path(__file__).resolve().parent
if len(sys.argv) != 3:
    raise SystemExit(
        "Usage: python run_dev073f_validation.py "
        "<fixture-path> <output-path>"
    )

FIXTURE = ROOT / sys.argv[1]
OUTPUT = ROOT / sys.argv[2]

if FIXTURE.resolve() == OUTPUT.resolve():
    raise SystemExit("Fixture and output paths must differ.")

if OUTPUT.exists():
    raise SystemExit(
        f"Refusing to overwrite existing validation file: {OUTPUT}"
    )

profiles = {profile.id: profile for profile in load_all_profiles()}

# DEV-073B: Load complete ability relationships.

special_rules = load_special_rules()
heroic_actions = load_heroic_actions()
spells = load_spells()
ability_tags = load_ability_tags()
ability_prerequisites = load_ability_prerequisites()

load_profile_special_rules(
    profiles,
    special_rules,
)

load_profile_heroic_actions(
    profiles,
    heroic_actions,
)

load_profile_spells(
    profiles,
    spells,
)

load_special_rule_tags(
    special_rules,
    ability_tags,
)

load_heroic_action_tags(
    heroic_actions,
    ability_tags,
)

load_spell_tags(
    spells,
    ability_tags,
)

load_heroic_action_prerequisites(
    heroic_actions,
    ability_prerequisites,
)

load_special_rule_prerequisites(
    special_rules,
    ability_prerequisites,
)

load_spell_prerequisites(
    spells,
    ability_prerequisites,
)

options = load_profile_options(profiles=profiles)

load_profile_option_wargear_assignments(options, load_wargear())
load_profile_option_mount_assignments(options, load_mounts())
load_profile_option_platform_assignments(options, load_platforms())
load_profile_option_state_effects(options)

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

from scenario_preservation_profile import (
    select_fog_of_war_preservation_model,
)

from army_manoeuvrability import calculate_army_manoeuvrability
from scenario_presence import calculate_army_scenario_presence

scenario_profiles = tuple(
    entry.configured_profile
    for entry in army.entries
    if entry.counts_as_model
    for _ in range(entry.quantity)
)

print(
    "Army manoeuvrability:",
    calculate_army_manoeuvrability(army),
)

from profile_metrics import calculate_profile_metrics

for entry in army.entries:
    if not entry.counts_as_model:
        continue

    metrics = calculate_profile_metrics(
        entry.configured_profile,
    )

    print(
        "Mobility contribution:",
        entry.profile.id,
        "quantity=", entry.quantity,
        "movement=", entry.configured_profile.effective_movement,
        "ability mobility=", metrics.mobility,
    )

    for assignment in entry.configured_profile.effective_special_rules:
        mobility_tags = [
            tag.weight
            for tag in assignment.rule.ability_tags
            if tag.tag.id == "MOBILITY"
        ]

        if mobility_tags:
            print(
                "  Mobility rule:",
                assignment.rule.id,
                "weights=", mobility_tags,
            )

print(
    "Scenario presence:",
    calculate_army_scenario_presence(scenario_profiles),
)
print(
    "Presence benchmark:",
    context.benchmark_presence,
)

from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
)

for entry in army.entries:
    if entry.profile.id != "DG_NEC":
        continue

    necromancer_preservation = (
        calculate_key_model_preservation_from_profile(
            profile=entry.profile,
            benchmark=context.combat_benchmark,
            benchmark_fate=context.benchmark_fate,
            army=army,
            army_list=result["army_list"],
        )
    )

    print(
        "Necromancer preservation:",
        necromancer_preservation.value,
    )

    from staying_power_capability import (
        calculate_staying_power_from_profile,
    )
    from key_model_preservation_capability import (
        calculate_protective_resources_from_fielded_model,
    )

    necromancer_model = next(
        model
        for model in army.fielded_models()
        if model.profile_id == "DG_NEC"
    )

    print(
        "Necromancer defensive survivability:",
        calculate_staying_power_from_profile(
            profile=entry.profile,
            benchmark=context.combat_benchmark,
        ),
    )

    print(
        "Necromancer protective resources:",
        calculate_protective_resources_from_fielded_model(
            army=army,
            fielded_model=necromancer_model,
            benchmark_fate=context.benchmark_fate,
            army_list=result["army_list"],
        ),
    )

from staying_power_capability import calculate_army_staying_power
from resource_capacity_score import calculate_resource_capacity_score

staying_power = calculate_army_staying_power(
    army=army,
    benchmark=context.combat_benchmark,
)

resource_capacity = calculate_resource_capacity_score(
    might=army.total_might(),
    will=army.total_will(),
    fate=army.total_fate(),
    army_points=army.total_points(),
)

print("Staying power:", staying_power)
print("Resource capacity:", resource_capacity)
print("Total Might:", army.total_might())
print("Total Will:", army.total_will())
print("Total Fate:", army.total_fate())
print("Army points:", army.total_points())
print(
    "State resilience:",
    (staying_power + resource_capacity) / 2,
)

from attrition_output_capability import (
    calculate_attrition_output_capability_from_army,
)

attrition = calculate_attrition_output_capability_from_army(
    army=result["army"],
    combat_benchmark=context.combat_benchmark,
    benchmark_combat_capability=context.benchmark_combat_capability,
)

print("Attrition output:", attrition.value)
print("Hero hunting:", inputs.hero_hunting)
print(
    "Key-model pressure:",
    (attrition.value + inputs.hero_hunting) / 2,
)

baseline = {
    "ticket": "DEV-073F",
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