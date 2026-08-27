from enum import Enum


class ObjectiveControlOverride(Enum):
    NONE = "none"
    AUTOMATIC_CONTROL = "automatic_control"


def resolve_objective_control_override(
    first_army_override: ObjectiveControlOverride,
    second_army_override: ObjectiveControlOverride,
) -> int | None:
    if not isinstance(
        first_army_override,
        ObjectiveControlOverride,
    ):
        raise TypeError(
            "first_army_override must be an ObjectiveControlOverride."
        )

    if not isinstance(
        second_army_override,
        ObjectiveControlOverride,
    ):
        raise TypeError(
            "second_army_override must be an ObjectiveControlOverride."
        )

    if (
        first_army_override
        is ObjectiveControlOverride.AUTOMATIC_CONTROL
        and second_army_override
        is ObjectiveControlOverride.NONE
    ):
        return 1

    if (
        second_army_override
        is ObjectiveControlOverride.AUTOMATIC_CONTROL
        and first_army_override
        is ObjectiveControlOverride.NONE
    ):
        return 2

    return None