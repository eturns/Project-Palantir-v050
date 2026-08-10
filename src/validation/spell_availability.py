from ability_availability import (
    ability_is_available,
)

from validation.output import (
    print_heading,
    print_pass,
)


def validate_spell_availability(
    necromancer,
    verbose: bool = False,
) -> None:
    """
    Validates spell availability for a profile.
    """

    results = {}

    for assignment in necromancer.spells:
        spell = assignment.spell

        available = ability_is_available(
            necromancer,
            spell,
        )

        assert available is True, (
            f"{spell.name} should be available "
            f"to {necromancer.name}"
        )

        results[spell.name] = available

    print_heading(
        "SPELL AVAILABILITY",
    )

    print_pass(
        "Spell availability validated",
    )

    if not verbose:
        return

    print()
    print("Spell Availability")
    print("------------------")

    for spell_name, available in results.items():
        print(
            f"{spell_name}: {available}"
        )