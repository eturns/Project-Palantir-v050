import sys

from army_combat_capability import (
    calculate_army_combat_capability,
)
from army_loader import (
    load_army_lists,
    load_factions,
)
from attrition_output_capability import (
    calculate_attrition_output_capability,
)
from combat_benchmark import (
    DEFAULT_COMBAT_BENCHMARK,
)
from loader import load_all_profiles
from relationship_loader import (
    load_profile_special_rules,
)
from rule_loader import load_special_rules
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

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            file_path,
            profiles_by_id,
            army_lists,
        )
    )

    combat_capability = (
        calculate_army_combat_capability(
            army=army,
            benchmark=DEFAULT_COMBAT_BENCHMARK,
        )
    )

    raw_ratio = (
        combat_capability
        / BENCHMARK_COMBAT_CAPABILITY
    )

    capability = (
        calculate_attrition_output_capability(
            combat_capability=combat_capability,
            benchmark_combat_capability=(
                BENCHMARK_COMBAT_CAPABILITY
            ),
        )
    )

    print()
    print(
        "========== ATTRITION OUTPUT DIAGNOSTIC =========="
    )
    print(
        f"Army: {definition.name}"
    )
    print(
        f"Models: {army.model_count()}"
    )
    print()
    print(
        f"Raw army combat capability: "
        f"{combat_capability:.6f}"
    )
    print(
        f"Benchmark combat capability: "
        f"{BENCHMARK_COMBAT_CAPABILITY:.3f}"
    )
    print(
        f"Raw ratio: {raw_ratio:.3f}"
    )
    print(
        f"Bounded Attrition Output: "
        f"{capability.value:.3f}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python "
            "src/run_attrition_output_diagnostic.py "
            "\"path\\to\\army.json\""
        )

    main(
        sys.argv[1],
    )