from enum import Enum


class ObjectiveControlOverride(Enum):
    NONE = "none"
    AUTOMATIC_CONTROL = "automatic_control"
    SHEER_DOMINANCE = "sheer_dominance"


def resolve_objective_control_override(
    first_army_override: ObjectiveControlOverride,
    second_army_override: ObjectiveControlOverride,
) -> int | None:
    """Return winning army, or None to retain ordinary presence resolution.

    SHEER_DOMINANCE outranks ordinary automatic control. Equal matching
    automatic effects retain the pre-existing cancellation behaviour.
    """
    if not isinstance(first_army_override, ObjectiveControlOverride):
        raise TypeError("first_army_override must be an ObjectiveControlOverride.")
    if not isinstance(second_army_override, ObjectiveControlOverride):
        raise TypeError("second_army_override must be an ObjectiveControlOverride.")
    rank = {
        ObjectiveControlOverride.NONE: 0,
        ObjectiveControlOverride.AUTOMATIC_CONTROL: 1,
        ObjectiveControlOverride.SHEER_DOMINANCE: 2,
    }
    first = rank[first_army_override]
    second = rank[second_army_override]
    if first == second:
        return None
    return 1 if first > second else 2
