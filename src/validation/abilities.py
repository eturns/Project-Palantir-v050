from ability_availability import (
    ability_is_available,
)

from validation.output import (
    print_heading,
    print_pass,
)


def validate_abilities(
    witch_king,
    heroic_actions,
    verbose: bool = False,
) -> None:
    """
    Validates heroic action availability for a profile.
    """

    expected_availability = {
        "HEROIC_MOVE": True,
        "HEROIC_SHOOT": False,
        "HEROIC_COMBAT": True,
        "HEROIC_STRIKE": True,
    }

    results = {}

    for action_id, expected in expected_availability.items():
        action = heroic_actions[action_id]

        available = ability_is_available(
            witch_king,
            action,
        )

        assert available is expected, (
            f"{action.name} availability was {available}; "
            f"expected {expected}"
        )

        results[action.name] = available

    print_heading(
        "ABILITY AVAILABILITY",
    )

    print_pass(
        "Heroic action availability validated",
    )

    if not verbose:
        return

    print()
    print("Ability Availability")
    print("--------------------")

    for action_name, available in results.items():
        print(
            f"{action_name}: {available}"
        )