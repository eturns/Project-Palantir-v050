from army import Army
from army_model_state import ArmyModelState


def get_initial_army_model_state(
    army: Army,
) -> ArmyModelState:
    model_count = army.model_count()

    return ArmyModelState(
        starting_models=model_count,
        remaining_models=model_count,
    )