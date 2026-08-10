from ability_queries import calculate_tag_score
from metric_constants import (
    METRIC_IDS,
    METRIC_LABELS,
    METRIC_NAMES,
    )


def validate_ability_metric_audit(
    special_rules,
    heroic_actions,
    spells,
    verbose: bool = False,
) -> None:
    """
    Validate that loaded abilities produce metric contributions
    from their assigned ability tags.
    """

    abilities = []

    abilities.extend(
        special_rules.values(),
    )

    abilities.extend(
        heroic_actions.values(),
    )

    abilities.extend(
        spells.values(),
    )

    assert abilities, (
        "No abilities were provided for metric auditing."
    )

    for ability in abilities:
        _validate_ability_tags(
            ability,
        )

    print()
    print(
        "========== ABILITY METRIC AUDIT =========="
    )
    print(
        f"✓ {len(abilities)} abilities audited"
    )

    if verbose:
        _print_ability_metric_audit(
            special_rules,
            heroic_actions,
            spells,
        )

def _validate_ability_tags(
    ability,
) -> None:

    assert hasattr(
        ability,
        "ability_tags",
    ), (
        f"Ability '{ability.name}' is missing "
        "'ability_tags'."
    )

    assert isinstance(
        ability.ability_tags,
        list,
    ), (
        f"Ability tags for '{ability.name}' "
        "must be a list."
    )

    for assignment in ability.ability_tags:

        assert assignment is not None, (
            f"Ability '{ability.name}' contains "
            "a missing tag assignment."
        )

        assert assignment.tag is not None, (
            f"Ability '{ability.name}' contains "
            "a missing tag."
        )

        metric_name = assignment.tag.id.lower()

        assert metric_name in METRIC_NAMES, (
            f"Ability '{ability.name}' uses unknown "
            f"metric tag '{assignment.tag.id}'."
        )

        assert isinstance(
            assignment.weight,
            (int, float),
        ), (
            f"Tag weight for '{ability.name}' "
            "must be numeric."
        )

        assert assignment.weight > 0, (
            f"Tag weight for '{ability.name}' "
            "must be positive."
        )

def _calculate_ability_metrics(
        ability,
    ) -> dict[str, float]:
    """
    Calculates every metric contribution for one ability.
    """

    return {
        metric_name: calculate_tag_score(
            [ability],
            METRIC_IDS[metric_name],
        )
        for metric_name in METRIC_NAMES
    }

def _print_ability_metric_audit(
    special_rules,
    heroic_actions,
    spells,
) -> None:

    _print_ability_group(
        "Special Rules",
        special_rules.values(),
    )

    _print_ability_group(
        "Heroic Actions",
        heroic_actions.values(),
    )

    _print_ability_group(
        "Spells",
        spells.values(),
    )

def _print_ability_group(
    heading,
    abilities,
) -> None:

    print()
    print(heading)
    print("-" * len(heading))

    for ability in abilities:

        metrics = _calculate_ability_metrics(
            ability,
        )

        print()
        print(ability.name)

        print("Assigned tags:")

        if ability.ability_tags:

            for assignment in ability.ability_tags:
                print(
                    f" - {assignment.tag.id}: "
                    f"{assignment.weight}"
                )

        else:
            print(" - None")

        print("Metric contributions:")

        non_zero_metrics = False

        for metric_name in METRIC_NAMES:

            value = metrics[
                metric_name
            ]

            if value == 0:
                continue

            non_zero_metrics = True

            print(
                f" - "
                f"{METRIC_LABELS[metric_name]}: "
                f"{value}"
            )

        if not non_zero_metrics:
            print(" - None")