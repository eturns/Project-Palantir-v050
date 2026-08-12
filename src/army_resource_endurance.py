from army_resource_state import ArmyResourceState
from army_resource_trajectory import ArmyResourceTrajectory
from resource_pacing_score import (
    calculate_resource_pacing_score,
)


def calculate_army_resource_endurance(
    resources: ArmyResourceState,
    trajectory: ArmyResourceTrajectory,
) -> float:
    scores = []

    if resources.might > 0:
        scores.append(
            calculate_resource_pacing_score(
                starting_resource=resources.might,
                remaining_by_turn=trajectory.might,
            )
        )

    if resources.will > 0:
        scores.append(
            calculate_resource_pacing_score(
                starting_resource=resources.will,
                remaining_by_turn=trajectory.will,
            )
        )

    if resources.fate > 0:
        scores.append(
            calculate_resource_pacing_score(
                starting_resource=resources.fate,
                remaining_by_turn=trajectory.fate,
            )
        )

    if not scores:
        return 0.0

    return sum(scores) / len(scores)