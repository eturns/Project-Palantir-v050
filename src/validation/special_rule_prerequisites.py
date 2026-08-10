from validation.output import (
    print_heading,
    print_pass,
)


def validate_special_rule_prerequisites(
    necromancer,
    verbose: bool = False,
) -> None:
    """
    Validates prerequisite assignments on a profile's
    special rules.
    """

    results = []

    for rule in necromancer.special_rules:
        prerequisites = [
            prerequisite.name
            for prerequisite in rule.prerequisites
        ]

        results.append(
            (
                rule.name,
                prerequisites,
            )
        )

    print_heading(
        "SPECIAL RULE PREREQUISITES",
    )

    print_pass(
        "Special rule prerequisites validated",
    )

    if not verbose:
        return

    print()
    print("Special Rule Prerequisites")
    print("--------------------------")

    for rule_name, prerequisites in results:
        print(f"\n{rule_name}")

        if prerequisites:
            for prerequisite_name in prerequisites:
                print(
                    f" - {prerequisite_name}"
                )
        else:
            print(" - No prerequisites")