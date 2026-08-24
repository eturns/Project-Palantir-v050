from army_effective_model_count import (
    calculate_effective_model_count,
)
from army_model_state import ArmyModelState


def calculate_break_point(
    starting_models: int,
) -> float:
    return starting_models / 2


def is_army_broken(
    state: ArmyModelState,
    counted_models: int = 0,
) -> bool:
    if state.starting_models == 0:
        return False

    effective_models = calculate_effective_model_count(
        state,
        counted_models=counted_models,
    )

    casualties = (
        state.starting_models
        - effective_models
    )

    return casualties > calculate_break_point(
        state.starting_models,
    )