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

from scenario_objective import ScenarioObjective

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

def test_scenario_goal_resolves_to_scenario_objective():
    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list="ARMY_LIST",
        combat_benchmark="COMBAT_BENCHMARK",
        key_profile="KEY_PROFILE",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    assert isinstance(
        objective,
        ScenarioObjective,
    )

    assert objective.army_list == "ARMY_LIST"
    assert objective.combat_benchmark == "COMBAT_BENCHMARK"
    assert objective.key_profile == "KEY_PROFILE"
    assert objective.benchmark_presence == 10
    assert objective.benchmark_manoeuvrability == 20
    assert objective.benchmark_combat_capability == 30
    assert objective.benchmark_fate == 40

def test_scenario_goal_requires_combat_benchmark():
    with pytest.raises(
        ValueError,
        match="Scenario optimisation requires a combat benchmark.",
    ):
        resolve_optimisation_goal_objective(
            goal=OptimisationGoal.SCENARIO,
            army_list="ARMY_LIST",
        )

def test_scenario_goal_requires_key_profile():
    with pytest.raises(
        ValueError,
        match="Scenario optimisation requires a key profile.",
    ):
        resolve_optimisation_goal_objective(
            goal=OptimisationGoal.SCENARIO,
            army_list="ARMY_LIST",
            combat_benchmark="COMBAT_BENCHMARK",
        )

def test_scenario_goal_requires_benchmark_presence():
    with pytest.raises(
        ValueError,
        match="Scenario optimisation requires benchmark presence.",
    ):
        resolve_optimisation_goal_objective(
            goal=OptimisationGoal.SCENARIO,
            army_list="ARMY_LIST",
            combat_benchmark="COMBAT_BENCHMARK",
            key_profile="KEY_PROFILE",
        )

def test_scenario_goal_requires_benchmark_manoeuvrability():
    with pytest.raises(
        ValueError,
        match="Scenario optimisation requires benchmark manoeuvrability.",
    ):
        resolve_optimisation_goal_objective(
            goal=OptimisationGoal.SCENARIO,
            army_list="ARMY_LIST",
            combat_benchmark="COMBAT_BENCHMARK",
            key_profile="KEY_PROFILE",
            benchmark_presence=10,           
        )

def test_scenario_goal_requires_benchmark_combat_capability():
    with pytest.raises(
        ValueError,
        match="Scenario optimisation requires benchmark combat capability.",
    ):
        resolve_optimisation_goal_objective(
            goal=OptimisationGoal.SCENARIO,
            army_list="ARMY_LIST",
            combat_benchmark="COMBAT_BENCHMARK",
            key_profile="KEY_PROFILE",
            benchmark_presence=10,
            benchmark_manoeuvrability=20,
        )

def test_scenario_goal_requires_benchmark_fate():
    with pytest.raises(
        ValueError,
        match="Scenario optimisation requires benchmark fate.",
    ):
        resolve_optimisation_goal_objective(
            goal=OptimisationGoal.SCENARIO,
            army_list="ARMY_LIST",
            combat_benchmark="COMBAT_BENCHMARK",
            key_profile="KEY_PROFILE",
            benchmark_presence=10,
            benchmark_manoeuvrability=20,
            benchmark_combat_capability=30,
        )

def test_scenario_and_balanced_goals_resolve_to_distinct_objectives():
    balanced_objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.BALANCED,
        army_list="ARMY_LIST",
        combat_benchmark="COMBAT_BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    scenario_objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list="ARMY_LIST",
        combat_benchmark="COMBAT_BENCHMARK",
        key_profile="KEY_PROFILE",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    assert isinstance(
        balanced_objective,
        BalancedObjective,
    )

    assert isinstance(
        scenario_objective,
        ScenarioObjective,
    )

    assert type(balanced_objective) is not type(
        scenario_objective
    )