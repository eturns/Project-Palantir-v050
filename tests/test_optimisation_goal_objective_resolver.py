import pytest

from army_list import ArmyList
from board_presence_objective import (
    BoardPresenceObjective,
)
from faction import Faction
from optimisation_goal_objective_resolver import (
    resolve_optimisation_goal_objective,
)
from optimisation_request import OptimisationGoal

from magic_objective import (
    MagicObjective,
)
from balanced_objective import BalancedObjective
from balanced_objective_preset import BALANCED_OBJECTIVE_PRESET
from battle_length_assumption import BattleHorizon
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from optimisation_goal_objective_resolver import (
    resolve_optimisation_goal_objective,
)
from optimisation_request import OptimisationGoal
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_strategy import ResourceStrategy

def test_board_presence_goal_resolves_to_board_presence_objective():
    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.BOARD_PRESENCE,
        army_list=army_list,
    )

    assert isinstance(
        objective,
        BoardPresenceObjective,
    )

    assert objective.army_list is army_list

def test_magic_goal_resolves_to_magic_objective():
    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.MAGIC,
        army_list=army_list,
    )

    assert isinstance(
        objective,
        MagicObjective,
    )

    assert objective.army_list is army_list

def test_balanced_goal_resolves_to_balanced_objective():
    resource_assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.BALANCED,
        army_list="ARMY_LIST",
        combat_benchmark=DEFAULT_COMBAT_BENCHMARK,
        resource_assumption=resource_assumption,
    )

    assert isinstance(
        objective,
        BalancedObjective,
    )

    assert objective.preset == BALANCED_OBJECTIVE_PRESET
    assert objective.army_list == "ARMY_LIST"
    assert objective.combat_benchmark == DEFAULT_COMBAT_BENCHMARK
    assert objective.resource_assumption == resource_assumption