"""DEV-077S-I2-C-H4: Real-army Defence comparison.

Read-only diagnostic.

Uses the production profile, wargear, mount, option and
army-list loaders. Does not change capability ratings,
scenario scores or source data.

Run from the repository root with PYTHONPATH=src.
"""

from pathlib import Path

from army_loader import (
    load_army_list_profiles,
    load_army_lists,
    load_factions,
)
from loader import load_all_profiles
from mechanical_defence_diagnostics import (
    calculate_mechanical_defence_diagnostics,
)
from mount_loader import load_mounts
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from profile_option_loader import (
    build_profile_options_by_external_id,
    load_profile_options,
)
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from profile_option_platform_loader import (
    load_profile_option_platform_assignments,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from model_platform_loader import load_platforms
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from wargear_loader import load_wargear
from rule_loader import load_special_rules

from relationship_loader import (
    load_profile_special_rules,
)

from profile_option_special_rule_loader import (
    load_profile_option_special_rules,
)


ARMIES = (
    (
        "Azog's Hunters — All Options",
        "tests/fixtures/azogs_hunters_all_options.json",
    ),
    (
        "Rise of the Necromancer — All Options",
        "tests/fixtures/rise_of_the_necromancer_all_options.json",
    ),
    (
        "Eddie's Choice",
        "src/eddies-choice.json",
    ),
)


def load_database():
    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(profiles_by_id)

    mounts = load_mounts()
    load_profile_option_mount_assignments(
        options,
        mounts,
    )

    wargear = load_wargear()
    load_profile_default_wargear(
        profiles=profiles_by_id,
        wargear=wargear,
    )
    load_profile_option_wargear_assignments(
        options,
        wargear,
    )

    platforms = load_platforms()
    load_profile_option_platform_assignments(
        options,
        platforms,
    )

    load_profile_option_state_effects(options)

    # Load the same special-rule relationships used by
    # Palantír's production application pathway.
    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    load_profile_option_special_rules(
        options,
        special_rules,
    )

    factions = load_factions()
    army_lists = load_army_lists(factions)

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(options)
    )

    return (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    )


def print_diagnostics(name, path, database):
    profiles, army_lists, options = database

    _, army, army_list = (
        import_army_from_mesbg_list_builder(
            path,
            profiles,
            army_lists,
            profile_options_by_external_id=options,
        )
    )

    result = calculate_mechanical_defence_diagnostics(
        army,
        engagements=3,
    )

    print()
    print("=" * 65)
    print(name)
    print("=" * 65)
    print(f"Army list:          {army_list.id}")
    print(f"Points:             {army.total_points()}")
    print(f"Models:             {army.model_count()}")
    print(f"Combat survival:    {result['combat_survival']:.4f}")
    print(f"Combat density:     {result['combat_density']:.4f}")
    print(f"Recovery presence:  {result['recovery_presence']:.4f}")
    print(f"Recovery density:   {result['recovery_density']:.4f}")
    print(
        "Recovery uplift:    "
        f"{result['recovery_presence'] - result['combat_survival']:.4f}"
    )

    print()
    print("Model breakdown:")

    for entry in army.entries:
        if not entry.counts_as_model:
            continue

        from profile_defensive_combat_score import (
            calculate_profile_defensive_combat_score,
        )
        from combat_benchmark import DEFAULT_COMBAT_BENCHMARK

        combat = calculate_profile_defensive_combat_score(
            entry.configured_profile,
            DEFAULT_COMBAT_BENCHMARK,
            engagements=3,
            include_resurrection=False,
        )

        recovery = calculate_profile_defensive_combat_score(
            entry.configured_profile,
            DEFAULT_COMBAT_BENCHMARK,
            engagements=3,
            include_resurrection=True,
        )

        print(
            f"  {entry.quantity:>2}x "
            f"{entry.configured_profile.profile.name[:32]:<32} "
            f"Combat={combat:.4f} "
            f"Recovery={recovery:.4f}"
        )

    print_sensitivity_analysis(army)
    print_strong_attacker_stress_test(army)

def print_sensitivity_analysis(army):
    """Compare Defence results at 1, 3 and 6 engagements."""

    from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
    from profile_defensive_combat_score import (
        calculate_profile_defensive_combat_score,
    )

    engagement_counts = (1, 3, 6)

    print()
    print("BENCHMARK SENSITIVITY")
    print("-" * 65)
    print(
        f"{'Engagements':<14}"
        f"{'Combat':>12}"
        f"{'Recovery':>12}"
        f"{'Uplift':>12}"
    )

    for count in engagement_counts:
        result = calculate_mechanical_defence_diagnostics(
            army,
            engagements=count,
        )

        combat = float(result["combat_survival"])
        recovery = float(result["recovery_presence"])

        print(
            f"{count:<14}"
            f"{combat:>12.4f}"
            f"{recovery:>12.4f}"
            f"{recovery - combat:>12.4f}"
        )

    print()
    print("SELECTED MODEL SENSITIVITY")
    print("-" * 65)

    target_names = (
        "azog",
        "bolg",
        "sauron",
        "necromancer",
        "dark headsman",
        "forsaken",
        "kham",
        "witch-king",
        "hunter orc warrior",
    )

    seen = set()

    for model in army.fielded_models():
        profile = model.configured_profile

        if profile is None:
            continue

        name = profile.profile.name

        if not any(
            target in name.lower()
            for target in target_names
        ):
            continue

        # Include each distinct configured model once.
        key = (
            profile.profile.id,
            tuple(
                option.id
                for option in profile.selected_options
            ),
        )

        if key in seen:
            continue

        seen.add(key)

        print()
        print(name)

        print(
            f"{'Engagements':<14}"
            f"{'Combat':>12}"
            f"{'Recovery':>12}"
        )

        for count in engagement_counts:
            combat = calculate_profile_defensive_combat_score(
                profile,
                DEFAULT_COMBAT_BENCHMARK,
                engagements=count,
                include_resurrection=False,
            )

            recovery = calculate_profile_defensive_combat_score(
                profile,
                DEFAULT_COMBAT_BENCHMARK,
                engagements=count,
                include_resurrection=True,
            )

            print(
                f"{count:<14}"
                f"{float(combat):>12.4f}"
                f"{float(recovery):>12.4f}"
            )

def print_strong_attacker_stress_test(army):
    """Read-only strong-attacker stress test for Defence v2."""

    from combat_benchmark import (
        CombatBenchmark,
        DEFAULT_COMBAT_BENCHMARK,
    )
    from profile_defensive_combat_score import (
        calculate_profile_defensive_combat_score,
    )

    benchmarks = (
        ("Standard", DEFAULT_COMBAT_BENCHMARK),
        (
            "Strong",
            CombatBenchmark(
                fight=5,
                strength=5,
                defence=6,
                attacks=2,
                wounds=1,
            ),
        ),
        (
            "Elite",
            CombatBenchmark(
                fight=7,
                strength=6,
                defence=6,
                attacks=3,
                wounds=1,
            ),
        ),
    )

    target_names = (
        "azog",
        "bolg",
        "sauron",
        "necromancer",
        "dark headsman",
        "forsaken",
        "kham",
        "witch-king",
        "hunter orc warrior",
    )

    print()
    print("STRONG-ATTACKER STRESS TEST")
    print("Three engagements per benchmark")
    print("=" * 70)

    seen = set()

    for fielded_model in army.fielded_models():
        profile = fielded_model.configured_profile

        if profile is None:
            continue

        name = profile.profile.name

        if not any(
            target in name.lower()
            for target in target_names
        ):
            continue

        key = (
            profile.profile.id,
            tuple(
                option.id
                for option in profile.selected_options
            ),
        )

        if key in seen:
            continue

        seen.add(key)

        print()
        print(name)
        print(
            f"{'Attacker':<12}"
            f"{'Combat':>12}"
            f"{'Recovery':>12}"
            f"{'Uplift':>12}"
        )

        previous_combat = None

        for label, benchmark in benchmarks:
            combat = float(
                calculate_profile_defensive_combat_score(
                    profile,
                    benchmark,
                    engagements=3,
                    include_resurrection=False,
                )
            )

            recovery = float(
                calculate_profile_defensive_combat_score(
                    profile,
                    benchmark,
                    engagements=3,
                    include_resurrection=True,
                )
            )

            print(
                f"{label:<12}"
                f"{combat:>12.4f}"
                f"{recovery:>12.4f}"
                f"{recovery - combat:>12.4f}"
            )

            if not (0 <= combat <= recovery <= 1):
                print("  WARNING: Probability bounds failed")

            if (
                previous_combat is not None
                and combat > previous_combat + 1e-9
            ):
                print("  WARNING: Stronger attacker increased survival")

            previous_combat = combat

def main():
    database = load_database()

    for name, path in ARMIES:
        if not Path(path).is_file():
            print(f"SKIPPED: {name} — file not found: {path}")
            continue

        try:
            print_diagnostics(name, path, database)
        except (ValueError, KeyError, TypeError) as error:
            print(
                f"\nFAILED: {name}\n"
                f"{type(error).__name__}: {error}"
            )


if __name__ == "__main__":
    main()
