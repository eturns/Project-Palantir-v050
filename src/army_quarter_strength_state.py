from army_effective_model_count import (
    calculate_effective_model_count,
)
from army_model_state import ArmyModelState


def calculate_quarter_strength(
    starting_models: int,
) -> float:
    return starting_models / 4


def is_army_at_or_below_quarter_strength(
    state: ArmyModelState,
    counted_models: int = 0,
) -> bool:
    if state.starting_models == 0:
        return False

    effective_models = calculate_effective_model_count(
        state,
        counted_models=counted_models,
    )

    return (
        effective_models
        <= calculate_quarter_strength(
            state.starting_models,
        )
    )