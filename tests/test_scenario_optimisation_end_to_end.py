from army import Army
from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from faction import Faction
from optimisation_goal_objective_resolver import (
    resolve_optimisation_goal_objective,
)
from optimisation_request import OptimisationGoal
from optimiser_candidate import OptimiserCandidate
from optimiser_evaluator import evaluate_candidate
from profiles import Profile
from scenario_objective import ScenarioObjective


def test_scenario_optimisation_runs_end_to_end():
    profile = Profile(
        id="SCENARIO_E2E",
        name="Scenario End To End Model",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=1,
    )

    army = Army()

    army.add_profile(
        profile,
        quantity=1,
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
        profiles=[profile],
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    candidate = OptimiserCandidate(
        army=army,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    assert isinstance(
        objective,
        ScenarioObjective,
    )

    evaluation = evaluate_candidate(
        candidate=candidate,
        objective=objective,
    )

    assert evaluation.candidate is candidate
    assert evaluation.errors == ()

    assert 0.0 <= evaluation.score <= 1.0

    score = objective.score(
        candidate,
    )

    assert score.total == evaluation.score
    assert len(score.contributions) == 6

    for contribution in score.contributions:
        assert 0.0 <= contribution.value <= 1.0