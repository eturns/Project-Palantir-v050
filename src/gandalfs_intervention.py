from shattered_spirit_transition import (
    resolve_shattered_spirit,
)


def resolve_shattered_spirit_with_gandalf(
    *,
    first_die: int,
    second_die: int,
    intelligence: str,
    within_three_inches_of_friendly_gandalf: bool,
    die_to_adjust: int | None = None,
    adjustment: int = 0,
):
    if not within_three_inches_of_friendly_gandalf:
        if die_to_adjust is not None or adjustment != 0:
            raise ValueError(
                "Gandalf's Intervention cannot be used "
                "unless Thráin is within 3 inches of "
                "a friendly Gandalf the Grey."
            )

        return resolve_shattered_spirit(
            first_die=first_die,
            second_die=second_die,
            intelligence=intelligence,
        )

    if die_to_adjust is None:
        if adjustment != 0:
            raise ValueError(
                "die_to_adjust is required when applying "
                "Gandalf's Intervention."
            )

        return resolve_shattered_spirit(
            first_die=first_die,
            second_die=second_die,
            intelligence=intelligence,
        )

    if die_to_adjust not in (1, 2):
        raise ValueError(
            "die_to_adjust must be 1 or 2."
        )

    if adjustment not in (-1, 1):
        raise ValueError(
            "adjustment must be -1 or 1."
        )

    adjusted_first_die = first_die
    adjusted_second_die = second_die

    if die_to_adjust == 1:
        adjusted_first_die += adjustment
    else:
        adjusted_second_die += adjustment

    if not 1 <= adjusted_first_die <= 6:
        raise ValueError(
            "Adjusted first die must remain between 1 and 6."
        )

    if not 1 <= adjusted_second_die <= 6:
        raise ValueError(
            "Adjusted second die must remain between 1 and 6."
        )

    return resolve_shattered_spirit(
        first_die=adjusted_first_die,
        second_die=adjusted_second_die,
        intelligence=intelligence,
    )