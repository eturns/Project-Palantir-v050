import sys

from army_loader import (
    load_army_lists,
    load_army_rules,
    load_factions,
)
from army_metric_densities import (
    calculate_army_metric_densities,
)
from battlefield_effects_input_builder import (
    build_battlefield_effects_inputs,
)
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from attrition_output_capability import (
    calculate_attrition_output_capability_from_army,
)
from key_model_pressure_capability import (
    calculate_key_model_pressure_from_army,
)
from loader import load_all_profiles
from objective_normalisation import (
    HERO_HUNTING_EFFECT_DENSITY_MAX,
)
from relationship_loader import (
    load_army_rule_tags,
    load_heroic_action_prerequisites,
    load_heroic_action_tags,
    load_profile_heroic_actions,
    load_profile_special_rules,
    load_profile_spells,
    load_special_rule_prerequisites,
    load_special_rule_tags,
    load_spell_prerequisites,
    load_spell_tags,
)
from rule_loader import (
    load_ability_prerequisites,
    load_ability_tags,
    load_heroic_actions,
    load_special_rules,
    load_spells,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)


BENCHMARK_COMBAT_CAPABILITY = 0.5


def main(file_path: str) -> None:
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    army_rules = load_army_rules(
    army_lists,
)

    heroic_actions = load_heroic_actions()
    spells = load_spells()
    ability_tags = load_ability_tags()
    ability_prerequisites = load_ability_prerequisites()

    load_profile_heroic_actions(
        profiles_by_id,
        heroic_actions,
    )

    load_profile_spells(
        profiles_by_id,
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

    load_army_rule_tags(
        army_rules,
        ability_tags,
    )

    load_heroic_action_prerequisites(
        heroic_actions,
        ability_prerequisites,
    )

    load_spell_prerequisites(
        spells,
        ability_prerequisites,
    )

    load_special_rule_prerequisites(
        special_rules,
        ability_prerequisites,
    )

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            file_path,
            profiles_by_id,
            army_lists,
        )
    )

    densities = calculate_army_metric_densities(
        army,
        army_list,
    )

    battlefield_effects = build_battlefield_effects_inputs(
        army=army,
        army_list=army_list,
    )

    attrition = (
        calculate_attrition_output_capability_from_army(
            army=army,
            combat_benchmark=DEFAULT_COMBAT_BENCHMARK,
            benchmark_combat_capability=(
                BENCHMARK_COMBAT_CAPABILITY
            ),
        )
    )

    pressure = calculate_key_model_pressure_from_army(
        army=army,
        army_list=army_list,
        combat_benchmark=DEFAULT_COMBAT_BENCHMARK,
        benchmark_combat_capability=(
            BENCHMARK_COMBAT_CAPABILITY
        ),
    )

    print()
    print(
        "========== KEY MODEL PRESSURE DIAGNOSTIC =========="
    )
    print(f"Army: {definition.name}")
    print()
    print(
        f"Raw Hero Hunting density: "
        f"{densities.hero_hunting:.6f}"
    )
    print(
        f"Hero Hunting maximum: "
        f"{HERO_HUNTING_EFFECT_DENSITY_MAX:.3f}"
    )
    print(
        f"Hero Hunting normalised: "
        f"{battlefield_effects.hero_hunting:.6f}"
    )
    print(
        f"Attrition Output: "
        f"{attrition.value:.6f}"
    )
    print(
        f"Key Model Pressure: "
        f"{pressure.value:.6f}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python "
            "src/run_key_model_pressure_diagnostic.py "
            "\"path\\to\\army.json\""
        )

    main(sys.argv[1])