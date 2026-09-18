from profiles import Profile
from relational_effect_condition import (
    RelationalEffectCondition,
    RelationalEffectConditionType,
)


def relational_effect_condition_matches(
    condition: RelationalEffectCondition,
    subject: Profile,
    related_model: Profile,
) -> bool:
    if (
        condition.condition_type
        is RelationalEffectConditionType
        .FRIENDLY_MODEL_DIFFERENT_RACE
    ):
        return subject.races.isdisjoint(
            related_model.races,
        )

    raise ValueError(
        "Unsupported relational effect condition type."
    )