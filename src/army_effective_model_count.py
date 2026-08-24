from army_model_state import ArmyModelState


def calculate_effective_model_count(
    state: ArmyModelState,
    counted_models: int = 0,
) -> int:
    effective_count = (
        state.remaining_models
        + counted_models
    )

    return min(
        effective_count,
        state.starting_models,
    )