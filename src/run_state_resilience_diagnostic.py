import sys

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from loader import load_all_profiles
from resource_capacity_score import (
    calculate_resource_capacity_score,
)
from staying_power_capability import (
    calculate_army_staying_power,
)
from state_resilience_capability import (
    calculate_state_resilience_capability,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from army_loader import (
    load_army_lists,
    load_factions,
)
from relationship_loader import (
    load_profile_special_rules,
)
from rule_loader import load_special_rules


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

    staying_power = calculate_army_staying_power(
        army=army,
        benchmark=DEFAULT_COMBAT_BENCHMARK,
    )

    resource_capacity = (
        calculate_resource_capacity_score(
            might=army.total_might(),
            will=army.total_will(),
            fate=army.total_fate(),
            army_points=army.total_points(),
        )
    )

    state_resilience = (
        calculate_state_resilience_capability(
            model_state_capacity=staying_power,
            resource_capacity=resource_capacity,
        )
    )

    print()
    print(
        "========== STATE RESILIENCE DIAGNOSTIC =========="
    )
    print(f"Army: {definition.name}")
    print(f"Models: {army.model_count()}")
    print(f"Points: {army.total_points()}")
    print()
    print(f"Total Might: {army.total_might()}")
    print(f"Total Will: {army.total_will()}")
    print(f"Total Fate: {army.total_fate()}")
    print()
    print(
        f"Staying Power: {staying_power:.6f}"
    )
    print(
        f"Resource Capacity: {resource_capacity:.6f}"
    )
    print(
        f"State Resilience: {state_resilience.value:.6f}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python "
            "src/run_state_resilience_diagnostic.py "
            "\"path\\to\\army.json\""
        )

    main(sys.argv[1])