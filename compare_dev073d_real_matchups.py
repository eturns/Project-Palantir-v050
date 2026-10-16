from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

# Reuse the loader setup from the existing validation runner.
# Stop before its analysis call so no validation JSON is rewritten.
runner = ROOT / "run_dev073b_validation.py"
source = runner.read_text(encoding="utf-8")
setup, separator, _ = source.partition(
    "result = analyse_mesbg_list_builder_file("
)

if not separator:
    raise RuntimeError("Could not locate the validation runner's analysis call.")

scope = {
    "__file__": str(runner),
    "__name__": "__dev073_setup__",
}
exec(compile(setup, str(runner), "exec"), scope)

from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from matchup_evaluator import calculate_matchup_result
from optimiser_candidate import OptimiserCandidate

army_lists = scope["load_army_lists"](scope["load_factions"]())
option_map = scope["build_profile_options_by_external_id"](
    scope["options"]
)

def import_fixture(filename):
    _, army, _ = import_army_from_mesbg_list_builder(
        str(ROOT / "tests" / "fixtures" / filename),
        scope["profiles"],
        army_lists,
        profile_options_by_external_id=option_map,
    )
    return army

dol_guldur = import_fixture("dol_guldur_700.json")
dale = import_fixture("garrison_of_dale.json")
five_armies = import_fixture("five_armies.json")
iron_hills = import_fixture("iron_hills_army.json")

comparisons = (
    ("Dol Guldur", dol_guldur, scope["profiles"]["DALE_GIRION"]),
    ("Dale", dale, scope["profiles"]["DG_NEC"]),
    ("Dol Guldur", dol_guldur, scope["profiles"]["IH_DAIN"]),
    ("Five Armies", five_armies, scope["profiles"]["DG_NEC"]),
    ("Iron Hills", iron_hills, scope["profiles"]["DG_NEC"]),
)

for name, army, target in comparisons:
    result = calculate_matchup_result(
        candidate=OptimiserCandidate(army=army),
        target_profile=target,
    )

    print(f"{name} ({army.model_count()} models)")
    print(f"  Target: {target.name} [{target.id}]")
    print(f"  Offence: {result.offensive_score:.6f}")
    print(f"  Defence: {result.defensive_score:.6f}")
    print(f"  Combined: {result.score:.6f}")

    from combat_benchmark import CombatBenchmark
from profile_offensive_combat_score import (
    calculate_profile_offensive_combat_score,
)

dain = scope["profiles"]["IH_DAIN"]

benchmark = CombatBenchmark(
    fight=dain.fight,
    strength=dain.strength,
    defence=dain.defence,
    attacks=dain.attacks,
    wounds=dain.wounds,
)

print("\nDol Guldur offence against Dain")
print(
    f"Target: F{dain.fight} S{dain.strength} "
    f"D{dain.defence} A{dain.attacks} W{dain.wounds}"
)

for entry in dol_guldur.entries:
    if not entry.counts_as_model:
        continue

    score = calculate_profile_offensive_combat_score(
        entry.profile,
        benchmark,
    )

    print(
        f"{entry.profile.id}: "
        f"quantity={entry.quantity}, "
        f"F{entry.profile.fight} "
        f"S{entry.profile.strength} "
        f"A{entry.profile.attacks}, "
        f"offence={score:.9f}"
    )

    from scenario_preservation_profile import (
    select_fog_of_war_preservation_model,
)
from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
)
from scenario_analysis_context import (
    build_default_scenario_analysis_context,
)

print("\nFog of War real-fixture check")

for filename, leader_id in (
    ("dol_guldur_700.json", "DG_NEC"),
    ("garrison_of_dale.json", "DALE_GIRION"),
):
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(ROOT / "tests" / "fixtures" / filename),
        scope["profiles"],
        army_lists,
        profile_options_by_external_id=option_map,
    )

    leader = next(
        model
        for model in army.fielded_models()
        if model.profile_id == leader_id
    )

    context = build_default_scenario_analysis_context(
        points_limit=army.total_points(),
    )

    selected = select_fog_of_war_preservation_model(
        army=army,
        leader_model=leader,
        combat_benchmark=context.combat_benchmark,
        benchmark_fate=context.benchmark_fate,
        army_list=army_list,
    )

    if selected is None:
        print(filename, "No eligible non-leader Hero")
        continue

    preservation = calculate_key_model_preservation_from_profile(
        profile=selected.configured_profile.profile,
        benchmark=context.combat_benchmark,
        benchmark_fate=context.benchmark_fate,
        army=army,
        army_list=army_list,
    )

    print(
        filename,
        "selected=", selected.profile_id,
        "preservation=", f"{preservation.value:.6f}",
    )

    from object_interaction import (
    ObjectInteractionMode,
    calculate_object_interaction_capability_from_army,
    count_uncovering_artifact_eligible_models,
)

print("\nIron Hills imported-fixture Heirloom check")
print("Models:", iron_hills.model_count())
print(
    "Eligible to uncover:",
    count_uncovering_artifact_eligible_models(iron_hills),
)
print(
    "Heirloom object interaction:",
    calculate_object_interaction_capability_from_army(
        iron_hills,
        ObjectInteractionMode.UNCOVER_AND_LIGHT_OBJECT,
    ),
)

from profile_metrics import calculate_profile_metrics

print("\nIron Hills ranged-wargear check")

for entry in iron_hills.entries:
    if entry.profile.id != "IH_WR":
        continue

    wargear_ids = {
        item.id
        for item in entry.configured_profile.effective_wargear
    }

    if "WG_CROSSBOW" not in wargear_ids:
        continue

    metrics = calculate_profile_metrics(entry.configured_profile)

    print("Crossbow Warriors:", entry.quantity)
    print("Effective wargear:", sorted(wargear_ids))
    print("Shooting metric:", metrics.shooting)

from projection_capability import (
    calculate_projection_capability_from_army,
)

_, iron_hills_army, iron_hills_list = (
    import_army_from_mesbg_list_builder(
        str(ROOT / "tests" / "fixtures" / "iron_hills_army.json"),
        scope["profiles"],
        army_lists,
        profile_options_by_external_id=option_map,
    )
)

print("\nIron Hills projection check")
print(
    "Projection:",
    calculate_projection_capability_from_army(
        iron_hills_army,
        iron_hills_list,
    ).value,
)

from army_manoeuvrability import calculate_army_manoeuvrability

print("\nIron Hills configured movement check")

for entry in iron_hills_army.entries:
    if entry.profile.id not in {"IH_DAIN", "IH_CAP"}:
        continue

    print(
        entry.profile.id,
        "mount=",
        (
            entry.configured_profile.effective_mount.id
            if entry.configured_profile.effective_mount is not None
            else None
        ),
        "platform=",
        (
            entry.configured_profile.effective_platform.id
            if entry.configured_profile.effective_platform is not None
            else None
        ),
        "movement=",
        entry.configured_profile.effective_movement,
        "base_size=",
        entry.configured_profile.effective_base_size_mm,
    )

print(
    "Army manoeuvrability:",
    calculate_army_manoeuvrability(iron_hills_army),
)

print("\nIron Hills Chariot structure")

for entry in iron_hills_army.entries:
    if entry.profile.id not in {"IH_CAP", "IH_CHARIOT"}:
        continue

    print(
        "profile=", entry.profile.id,
        "quantity=", entry.quantity,
        "counts_as_model=", entry.counts_as_model,
        "movement=", entry.configured_profile.effective_movement,
        "base_size=", entry.configured_profile.effective_base_size_mm,
        "platform=",
        (
            entry.configured_profile.effective_platform.id
            if entry.configured_profile.effective_platform is not None
            else None
        ),
    )

print("\nIron Hills actual Heirloom check")
print(
    "Heirloom object interaction:",
    calculate_object_interaction_capability_from_army(
        iron_hills_army,
        ObjectInteractionMode.SEARCH_AND_LIGHT_OBJECT,
    ),
)