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
from scenario_context import ScenarioContext
from resurrection_config import ResurrectionConfig

SCENARIO_MEAN_WEIGHT = 0.75
SCENARIO_MINIMUM_WEIGHT = 0.25


@dataclass(frozen=True)
class ScenarioObjective(OptimiserObjective):
    context: ScenarioContext | None = None
    resurrection_config: ResurrectionConfig | None = None
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

        context = self.context
        resurrection_config = self.resurrection_config

        if summary_builder is None:
            summary = build_scenario_pool_fit_summary_from_candidate(
                candidate=candidate,
                context=context,
                resurrection_config=resurrection_config,
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