from dataclasses import dataclass
from typing import Callable

from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective
from scenario_candidate_summary import (
    build_scenario_pool_fit_summary_from_candidate,
)
from scenario_pool_fit import ScenarioPoolFitSummary


SCENARIO_MEAN_WEIGHT = 0.75
SCENARIO_MINIMUM_WEIGHT = 0.25


@dataclass(frozen=True)
class ScenarioObjective(OptimiserObjective):
    army_list: object = None
    key_profile: object = None
    combat_benchmark: object = None
    benchmark_presence: int | float | None = None
    benchmark_manoeuvrability: int | float | None = None
    benchmark_combat_capability: int | float | None = None
    benchmark_fate: int | float | None = None
    resurrection_config: dict | None = None
    summary_builder: (
        Callable[
            [OptimiserCandidate],
            ScenarioPoolFitSummary,
        ]
        | None
    ) = None

    def score(
        self,
        candidate: OptimiserCandidate,
    ) -> ObjectiveScore:
        summary_builder = self.summary_builder

        if summary_builder is None:
            summary = build_scenario_pool_fit_summary_from_candidate(
                candidate=candidate,
                army_list=self.army_list,
                key_profile=self.key_profile,
                combat_benchmark=self.combat_benchmark,
                benchmark_presence=self.benchmark_presence,
                benchmark_manoeuvrability=(
                    self.benchmark_manoeuvrability
                ),
                benchmark_combat_capability=(
                    self.benchmark_combat_capability
                ),
                benchmark_fate=self.benchmark_fate,
                resurrection_config=self.resurrection_config,
            )
        else:
            summary = summary_builder(
                candidate,
            )

        mean_pool_score = sum(
            pool_result.score
            for pool_result in summary.pool_results
        ) / len(summary.pool_results)

        total = (
            mean_pool_score
            * SCENARIO_MEAN_WEIGHT
            + summary.weakest.score
            * SCENARIO_MINIMUM_WEIGHT
        )

        contributions = tuple(
            ObjectiveContribution(
                name=pool_result.pool.value,
                value=pool_result.score,
            )
            for pool_result in summary.pool_results
        )

        return ObjectiveScore(
            total=total,
            contributions=contributions,
        )

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        return self.score(
            candidate,
        ).total