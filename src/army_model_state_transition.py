from army_model_state import ArmyModelState


def apply_model_casualties(
    state: ArmyModelState,
    casualties: int,
) -> ArmyModelState:
    if casualties < 0:
        raise ValueError(
            "Casualty count cannot be negative."
        )

    if casualties > state.remaining_models:
        raise ValueError(
            "Casualty count cannot exceed remaining model count."
        )

    return ArmyModelState(
        starting_models=state.starting_models,
        remaining_models=(
            state.remaining_models
            - casualties
        ),
    )