"""DEV-077S-I2-D-C3: read-only real-fixture Mobility comparison.

Run from the project root:
  py -3.14 tools/i2d_c3_real_army_mobility_validation.py

The first two rows import real production JSON fixtures; the third row is a
clearly labelled synthetic infantry control, NOT a legal competitive roster.
No scenario, dashboard or scoring module is modified.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT, ROOT / "src"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from army import Army
from configured_profile import ConfiguredProfile
from army_mobility_aggregation import aggregate_army_mobility
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from loader import load_all_profiles
from army_loader import load_army_list_profiles, load_army_lists, load_factions
from profile_option_loader import build_profile_options_by_external_id, load_profile_options
from mount_loader import load_mounts
from profile_default_mount_loader import load_profile_default_mounts
from profile_option_mount_loader import load_profile_option_mount_assignments
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from profile_option_state_effect_loader import load_profile_option_state_effects
from relationship_loader import load_profile_special_rules, load_profile_heroic_actions
from rule_loader import load_special_rules, load_heroic_actions

FIXTURES = (
    ("Rise of the Necromancer (fixture)", "rise_of_the_necromancer_all_options.json"),
    ("Azog's Hunters (fixture)", "azogs_hunters_all_options.json"),
)


def load_production_data():
    profiles = {p.id: p for p in load_all_profiles()}
    mounts = load_mounts()
    options = load_profile_options(profiles=profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_default_mounts(profiles=profiles, mounts=mounts)
    load_profile_option_mount_assignments(profile_options=options, mounts=mounts)
    load_profile_option_wargear_assignments(profile_options=options, wargear=wargear)
    load_profile_option_state_effects(profile_options=options)
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    load_profile_heroic_actions(profiles=profiles, heroic_actions=load_heroic_actions())
    factions = load_factions()
    lists = load_army_lists(factions)
    load_army_list_profiles(army_lists=lists, profiles_by_id=profiles)
    return profiles, lists, build_profile_options_by_external_id(options)


def summarise(label, army, source):
    result = aggregate_army_mobility(army)
    return {
        "army": label,
        "source": source,
        "points": result.army_points,
        "models": result.model_count,
        "legacy_average": round(result.legacy_average, 5),
        "open_average": round(result.average_open_ground, 5),
        "difficult_average": round(result.average_difficult_terrain, 5),
        "terrain_retention": round(result.terrain_retention, 5),
        "open_total": round(result.total_open_ground, 5),
        "terrain_total": round(result.total_difficult_terrain, 5),
        "open_per_100_points": round(result.open_ground_per_100_points, 5),
        "difficult_per_100_points": round(result.difficult_terrain_per_100_points, 5),
        "self_reposition_models": result.self_reposition_models,
        "anchor_models": result.anchor_reposition_models,
        "potential_anchor_pairs": result.eligible_anchor_pairs,
    }


def create_comparison():
    profiles, army_lists, options = load_production_data()
    rows = []
    for label, filename in FIXTURES:
        path = ROOT / "tests" / "fixtures" / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required production fixture not found: {path}")
        _definition, army, _army_list = import_army_from_mesbg_list_builder(
            str(path), profiles_by_id=profiles,
            army_lists_by_id=army_lists, profile_options_by_external_id=options,
        )
        rows.append(summarise(label, army, str(path.relative_to(ROOT))))

    # Intentionally not presented as a valid army list; controls for the effect
    # of quantity on model-average, total and points-density measures.
    control = Army()
    control.add_configured_profile(ConfiguredProfile(profile=profiles["DG_HOW"]), quantity=12)
    rows.append(summarise("Hunter Orc infantry control (synthetic)", control,
                          "12 x DG_HOW; synthetic, not a validated army roster"))
    return rows


def main():
    rows = create_comparison()
    destination = ROOT / "i2d_c3_real_army_mobility_comparison.csv"
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {destination}")
    for row in rows:
        print(f'\n{row["army"]}: {row["points"]} pts; {row["models"]} models')
        print(f'  Legacy={row["legacy_average"]:.3f}  Open={row["open_average"]:.3f}  '
              f'Difficult={row["difficult_average"]:.3f}  Retention={row["terrain_retention"]:.2%}')
        print(f'  Open/100pts={row["open_per_100_points"]:.3f}  '
              f'Difficult/100pts={row["difficult_per_100_points"]:.3f}')
        print(f'  Reposition: self={row["self_reposition_models"]}; '
              f'anchor models={row["anchor_models"]}; potential pairs={row["potential_anchor_pairs"]}')
    print("\nDiagnostic only. No blended mobility score, positional benefit, or ranking is implied.")


if __name__ == "__main__":
    main()
