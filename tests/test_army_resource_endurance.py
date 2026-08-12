import pytest

import army_resource_endurance

from army_resource_state import ArmyResourceState
from army_resource_trajectory import (
    ArmyResourceTrajectory,
)


def test_army_resource_endurance_averages_active_resource_pools(
    monkeypatch,
):
    resources = ArmyResourceState(
        might=4,
        will=4,
        fate=4,
    )

    trajectory = ArmyResourceTrajectory(
        might=(3, 2, 1, 0),
        will=(4, 2, 1, 0),
        fate=(4, 4, 2, 0),
    )

    scores = {
        (3, 2, 1, 0): 1.0,
        (4, 2, 1, 0): 0.8,
        (4, 4, 2, 0): 0.6,
    }

    monkeypatch.setattr(
        army_resource_endurance,
        "calculate_resource_pacing_score",
        lambda starting_resource, remaining_by_turn: scores[
            remaining_by_turn
        ],
    )

    score = (
        army_resource_endurance
        .calculate_army_resource_endurance(
            resources,
            trajectory,
        )
    )

    assert score == pytest.approx(0.8)


def test_zero_starting_resource_pools_are_excluded():
    resources = ArmyResourceState(
        might=4,
        will=0,
        fate=0,
    )

    trajectory = ArmyResourceTrajectory(
        might=(3, 2, 1, 0),
        will=(0, 0, 0, 0),
        fate=(0, 0, 0, 0),
    )

    score = (
        army_resource_endurance
        .calculate_army_resource_endurance(
            resources,
            trajectory,
        )
    )

    assert score == pytest.approx(1.0)


def test_army_with_no_resources_has_zero_endurance():
    resources = ArmyResourceState(
        might=0,
        will=0,
        fate=0,
    )

    trajectory = ArmyResourceTrajectory(
        might=(0, 0, 0, 0),
        will=(0, 0, 0, 0),
        fate=(0, 0, 0, 0),
    )

    score = (
        army_resource_endurance
        .calculate_army_resource_endurance(
            resources,
            trajectory,
        )
    )

    assert score == 0.0