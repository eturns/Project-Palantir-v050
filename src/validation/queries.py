from queries import (
    find_profile,
    highest_value,
    profiles_costing,
    profiles_with_minimum_value,
)

from validation.output import (
    print_heading,
    print_pass,
)


def validate_queries(
    profiles,
    verbose: bool = False,
) -> None:
    """
    Validates profile query functions.
    """

    eighty_point_profiles = profiles_costing(
        profiles,
        80,
    )

    witch_king = find_profile(
        profiles,
        "DG_WK",
    )

    strong_fighters = profiles_with_minimum_value(
        profiles,
        "fight",
        5,
    )

    highest_fight = highest_value(
        profiles,
        "fight",
    )

    highest_strength = highest_value(
        profiles,
        "strength",
    )

    highest_defence = highest_value(
        profiles,
        "defence",
    )

    print_heading(
        "QUERIES",
    )

    print_pass(
        "Profile queries completed successfully",
    )

    if not verbose:
        return

    print()
    print(f"Highest Fight value   : {highest_fight}")
    print(f"Highest Strength value: {highest_strength}")
    print(f"Highest Defence value : {highest_defence}")

    print()
    print("Profiles costing 80 points:")
    for profile in eighty_point_profiles:
        print(f" - {profile.name}")

    print()
    print("Profile found by ID:")
    print(f" - {witch_king.id}: {witch_king.name}")

    print()
    print("Profiles with Fight 5 or higher:")
    for profile in strong_fighters:
        print(
            f" - F{profile.fight}: {profile.name}"
        )