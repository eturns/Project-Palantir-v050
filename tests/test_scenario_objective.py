from optimiser_candidate import OptimiserCandidate
from scenario_definition import ScenarioPool
from scenario_objective import (
    SCENARIO_MEAN_WEIGHT,
    SCENARIO_MINIMUM_WEIGHT,
    ScenarioObjective,
)
from scenario_pool_fit import (
    ScenarioPoolFitResult,
    ScenarioPoolFitSummary,
)
from optimiser_evaluator import evaluate_candidate
from optimiser_ranking import rank_evaluations

def test_scenario_objective_returns_mean_pool_score():
    summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.2,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.6,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=1.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.0,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.MANOEUVRING,
            score=1.0,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.UNIQUE,
            score=0.0,
        ),
    )

    objective = ScenarioObjective(
        summary_builder=lambda candidate: summary,
    )

    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    result = objective.evaluate(candidate)

    assert result == 0.375


def test_scenario_objective_score_exposes_pool_contributions():
    summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.2,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.6,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=1.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.0,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.MANOEUVRING,
            score=1.0,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.UNIQUE,
            score=0.0,
        ),
    )

    objective = ScenarioObjective(
        summary_builder=lambda candidate: summary,
    )

    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    result = objective.score(candidate)

    assert result.total == 0.375

    assert tuple(
        contribution.name
        for contribution in result.contributions
    ) == tuple(
        pool.value
        for pool in ScenarioPool
    )

    assert tuple(
        contribution.value
        for contribution in result.contributions
    ) == (
        0.2,
        0.4,
        0.6,
        0.8,
        1.0,
        0.0,
    )


def test_scenario_objective_distinguishes_equal_means_by_weakest_pool():
    balanced_summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.5,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
    )

    uneven_summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=1.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=1.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.0,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=1.0,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.MANOEUVRING,
            score=0.0,
        ),
    )

    balanced_objective = ScenarioObjective(
        summary_builder=lambda candidate: balanced_summary,
    )

    uneven_objective = ScenarioObjective(
        summary_builder=lambda candidate: uneven_summary,
    )

    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    assert balanced_objective.evaluate(candidate) == 0.5
    assert uneven_objective.evaluate(candidate) == 0.375


def test_scenario_objective_rewards_better_weakest_pool_when_means_are_equal():
    balanced_summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.5,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
    )

    uneven_summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=1.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=1.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.0,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.0,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=1.0,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.MANOEUVRING,
            score=0.0,
        ),
    )

    balanced_objective = ScenarioObjective(
        summary_builder=lambda candidate: balanced_summary,
    )

    uneven_objective = ScenarioObjective(
        summary_builder=lambda candidate: uneven_summary,
    )

    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    assert (
        balanced_objective.evaluate(candidate)
        > uneven_objective.evaluate(candidate)
    )

def test_scenario_objective_uses_default_summary_builder(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.5,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
    )

    captured = {}

    def fake_default_summary_builder(
        *,
        candidate,
        **kwargs,
    ):
        captured["candidate"] = candidate
        return summary

    monkeypatch.setattr(
        "scenario_objective."
        "build_scenario_pool_fit_summary_from_candidate",
        fake_default_summary_builder,
    )

    objective = ScenarioObjective()

    result = objective.evaluate(
        candidate,
    )

    assert captured["candidate"] is candidate
    assert result == 0.5

def test_scenario_objective_passes_scenario_inputs_to_default_summary_builder(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.5,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
    )

    captured = {}

    def fake_default_summary_builder(
        *,
        candidate,
        army_list,
        key_profile,
        combat_benchmark,
        benchmark_presence,
        benchmark_manoeuvrability,
        benchmark_combat_capability,
        benchmark_fate,
        resurrection_config,
    ):
        captured.update(
            {
                "candidate": candidate,
                "army_list": army_list,
                "key_profile": key_profile,
                "combat_benchmark": combat_benchmark,
                "benchmark_presence": benchmark_presence,
                "benchmark_manoeuvrability": benchmark_manoeuvrability,
                "benchmark_combat_capability": benchmark_combat_capability,
                "benchmark_fate": benchmark_fate,
                "resurrection_config": resurrection_config,
            }
        )

        return summary

    monkeypatch.setattr(
        "scenario_objective."
        "build_scenario_pool_fit_summary_from_candidate",
        fake_default_summary_builder,
    )

    objective = ScenarioObjective(
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
        resurrection_config={
            "test": True,
        },
    )

    result = objective.evaluate(
        candidate,
    )

    assert captured == {
        "candidate": candidate,
        "army_list": "ARMY_LIST",
        "key_profile": "KEY_PROFILE",
        "combat_benchmark": "COMBAT_BENCHMARK",
        "benchmark_presence": 10,
        "benchmark_manoeuvrability": 20,
        "benchmark_combat_capability": 30,
        "benchmark_fate": 40,
        "resurrection_config": {
            "test": True,
        },
    }

    assert result == 0.5

def test_scenario_objective_integrates_with_optimiser_evaluator():
    summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.5,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.5,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.5,
        ),
    )

    objective = ScenarioObjective(
        summary_builder=lambda candidate: summary,
    )

    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    result = evaluate_candidate(
        candidate=candidate,
        objective=objective,
    )

    assert result.candidate is candidate
    assert result.score == 0.5
    assert result.errors == ()

def test_scenario_objective_scores_drive_optimiser_ranking():
    stronger_summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.8,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.8,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.8,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.8,
        ),
    )

    weaker_summary = ScenarioPoolFitSummary(
        pool_results=(
            ScenarioPoolFitResult(
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.KILL_THE_ENEMY,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MAELSTROM_OF_BATTLE,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.OBJECT,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.MANOEUVRING,
                score=0.4,
            ),
            ScenarioPoolFitResult(
                pool=ScenarioPool.UNIQUE,
                score=0.4,
            ),
        ),
        strongest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.4,
        ),
        weakest=ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.4,
        ),
    )

    stronger_candidate = OptimiserCandidate(
        army="STRONGER_ARMY",
    )

    weaker_candidate = OptimiserCandidate(
        army="WEAKER_ARMY",
    )

    def summary_builder(candidate):
        if candidate is stronger_candidate:
            return stronger_summary

        return weaker_summary

    objective = ScenarioObjective(
        summary_builder=summary_builder,
    )

    stronger_evaluation = evaluate_candidate(
        candidate=stronger_candidate,
        objective=objective,
    )

    weaker_evaluation = evaluate_candidate(
        candidate=weaker_candidate,
        objective=objective,
    )

    ranked = rank_evaluations(
        evaluations=(
            weaker_evaluation,
            stronger_evaluation,
        ),
    )

    assert ranked == (
        stronger_evaluation,
        weaker_evaluation,
    )

    assert ranked[0].score == 0.8
    assert ranked[1].score == 0.4

def test_scenario_objective_uses_calibrated_75_25_weighting():
    assert SCENARIO_MEAN_WEIGHT == 0.75
    assert SCENARIO_MINIMUM_WEIGHT == 0.25
    assert (
        SCENARIO_MEAN_WEIGHT
        + SCENARIO_MINIMUM_WEIGHT
        == 1.0
    )