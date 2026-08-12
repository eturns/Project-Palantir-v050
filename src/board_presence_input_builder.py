from army import Army
from army_list import ArmyList

from army_manoeuvrability import (
    calculate_army_manoeuvrability,
)
from army_metric_densities import (
    calculate_army_metric_densities,
)
from board_presence_inputs import (
    BoardPresenceInputs,
)
from objective_normalisation import (
    normalise_model_presence,
    normalise_manoeuvrability,
    normalise_control,
)


def build_board_presence_inputs(
    army: Army,
    army_list: ArmyList,
) -> BoardPresenceInputs:
    army_points = army.total_points()

    model_presence = normalise_model_presence(
        model_count=army.model_count(),
        army_points=army_points,
    )

    manoeuvrability = normalise_manoeuvrability(
        manoeuvrability=(
            calculate_army_manoeuvrability(
                army,
            )
        ),
    )

    metric_densities = (
        calculate_army_metric_densities(
            army,
            army_list,
        )
    )

    control = normalise_control(
        control_density=metric_densities.control,
    )

    return BoardPresenceInputs(
        model_presence=model_presence,
        manoeuvrability=manoeuvrability,
        control=control,
    )