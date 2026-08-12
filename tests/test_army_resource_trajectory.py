from army_resource_state import ArmyResourceState
from army_resource_trajectory import (
    ArmyResourceTrajectory,
    calculate_army_resource_trajectory,
)
from battle_length_assumption import BattleHorizon
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_strategy import ResourceStrategy


def test_army_resource_trajectory_uses_explicit_horizon_and_strategy():
    resources = ArmyResourceState(
        might=6,
        will=3,
        fate=0,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.SHORT,
        strategy=ResourceStrategy.BALANCED,
    )

    trajectory = calculate_army_resource_trajectory(
        resources,
        assumption,
    )

    assert trajectory == ArmyResourceTrajectory(
        might=(5, 4, 3, 2, 1, 0),
        will=(2, 1, 0, 0, 0, 0),
        fate=(0, 0, 0, 0, 0, 0),
    )


def test_army_resource_trajectory_contains_one_state_per_assumed_turn():
    resources = ArmyResourceState(
        might=8,
        will=8,
        fate=8,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    trajectory = calculate_army_resource_trajectory(
        resources,
        assumption,
    )

    assert len(trajectory.might) == 8
    assert len(trajectory.will) == 8
    assert len(trajectory.fate) == 8