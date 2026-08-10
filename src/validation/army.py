# ============================================================================
# Imports
# ============================================================================

from validation.output import (
    print_fail,
    print_heading,
    print_pass,
)


# ============================================================================
# Public Functions
# ============================================================================

def validate_army(
    army,
    verbose: bool = False,
    max_points: int = 700,
) -> None:
    """Validate an Army and optionally print diagnostic details."""

    print_heading(
        "ARMY",
    )

    errors = army.validate(
        max_points,
    )

    if errors:
        for error in errors:
            print_fail(
                error,
            )
    else:
        print_pass(
            "Army is valid",
        )

    if not verbose:
        return

    print()
    print(f"Profiles in army : {army.profile_count()}")
    print(f"Army points      : {army.total_points()}")
    print(f"Army Might       : {army.total_might()}")
    print(f"Army Will        : {army.total_will()}")
    print(f"Army Fate        : {army.total_fate()}")

    highest_fight = army.highest_fight()
    highest_strength = army.highest_strength()
    highest_defence = army.highest_defence()

    print()
    print("Highest values:")
    print(
        f"Highest Fight   : F{highest_fight.fight} "
        f"({highest_fight.name})"
    )
    print(
        f"Highest Strength: S{highest_strength.strength} "
        f"({highest_strength.name})"
    )
    print(
        f"Highest Defence : D{highest_defence.defence} "
        f"({highest_defence.name})"
    )

    lowest_fight = army.lowest_fight()
    lowest_strength = army.lowest_strength()
    lowest_defence = army.lowest_defence()

    print()
    print("Lowest values:")
    print(
        f"Lowest Fight    : F{lowest_fight.fight} "
        f"({lowest_fight.name})"
    )
    print(
        f"Lowest Strength : S{lowest_strength.strength} "
        f"({lowest_strength.name})"
    )
    print(
        f"Lowest Defence  : D{lowest_defence.defence} "
        f"({lowest_defence.name})"
    )
