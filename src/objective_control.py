from objective_control_override import (
    ObjectiveControlOverride,
    resolve_objective_control_override,
)


def resolve_objective_control(
    first_army_presence: int | float,
    second_army_presence: int | float,
    first_army_override: ObjectiveControlOverride,
    second_army_override: ObjectiveControlOverride,
) -> int | None:
    if (
        not isinstance(first_army_presence, (int, float))
        or isinstance(first_army_presence, bool)
    ):
        raise TypeError(
            "first_army_presence must be int or float."
        )

    if (
        not isinstance(second_army_presence, (int, float))
        or isinstance(second_army_presence, bool)
    ):
        raise TypeError(
            "second_army_presence must be int or float."
        )

    if first_army_presence < 0:
        raise ValueError(
            "first_army_presence cannot be negative."
        )

    if second_army_presence < 0:
        raise ValueError(
            "second_army_presence cannot be negative."
        )

    override_result = resolve_objective_control_override(
        first_army_override=first_army_override,
        second_army_override=second_army_override,
    )

    if override_result is not None:
        return override_result

    if first_army_presence > second_army_presence:
        return 1

    if second_army_presence > first_army_presence:
        return 2

    return None
