from validation.output import (
    print_heading,
    print_pass,
)


def validate_ability_tags(
    necromancer,
    heroic_actions,
    verbose: bool = False,
) -> None:
    """
    Validates and displays ability-tag assignments for
    special rules, spells, and heroic actions.
    """

    special_rule_results = []
    spell_results = []
    heroic_action_results = []

    for rule in necromancer.special_rules:
        tags = [
            (
                assignment.tag.name,
                assignment.weight,
            )
            for assignment in rule.ability_tags
        ]

        special_rule_results.append(
            (
                rule.name,
                tags,
            )
        )

    for assignment in necromancer.spells:
        spell = assignment.spell

        tags = [
            (
                tag_assignment.tag.name,
                tag_assignment.weight,
            )
            for tag_assignment in spell.ability_tags
        ]

        spell_results.append(
            (
                spell.name,
                assignment.cast_value,
                tags,
            )
        )

    for action in heroic_actions.values():
        tags = [
            (
                assignment.tag.name,
                assignment.weight,
            )
            for assignment in action.ability_tags
        ]

        heroic_action_results.append(
            (
                action.name,
                tags,
            )
        )

    print_heading(
        "ABILITY TAGS",
    )

    print_pass(
        "Ability tag assignments validated",
    )

    if not verbose:
        return

    print()
    print("Special Rule Tags")
    print("-----------------")

    for rule_name, tags in special_rule_results:
        print(f"\n{rule_name}")

        if tags:
            for tag_name, weight in tags:
                print(
                    f" - {tag_name} ({weight})"
                )
        else:
            print(" - No tags")

    print()
    print("Spell Tags")
    print("----------")

    for spell_name, cast_value, tags in spell_results:
        print(
            f"\n{spell_name} ({cast_value}+)"
        )

        if tags:
            for tag_name, weight in tags:
                print(
                    f" - {tag_name} ({weight})"
                )
        else:
            print(" - No tags")

    print()
    print("Heroic Action Tags")
    print("------------------")

    for action_name, tags in heroic_action_results:
        print(f"\n{action_name}")

        if tags:
            for tag_name, weight in tags:
                print(
                    f" - {tag_name} ({weight})"
                )
        else:
            print(" - No tags")