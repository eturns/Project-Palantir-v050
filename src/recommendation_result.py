"""
Project Palantír
================

File:
    recommendation_result.py

Purpose:
    Represents one ranked, explainable optimiser recommendation.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass

from objective_capability_assessment import (
    assess_objective_contribution,
)
from objective_score import ObjectiveScore
from optimiser_candidate import OptimiserCandidate
from recommendation_capabilities import (
    find_strongest_contributions,
    find_weakest_contributions,
)
from marginal_swap_result import MarginalSwapResult
from sensitivity_stability import SensitivityStability

@dataclass(frozen=True)
class RecommendationResult:
    candidate: OptimiserCandidate
    rank: int
    objective_score: ObjectiveScore
    constraint_errors: tuple[str, ...] = ()
    marginal_swaps: tuple[MarginalSwapResult, ...] = ()
    sensitivity_stability: SensitivityStability | None = None

    @property
    def strengths(self):
        return find_strongest_contributions(
            self.objective_score,
        )

    @property
    def weaknesses(self):
        return find_weakest_contributions(
            self.objective_score,
        )

    @property
    def capabilities(self):
        return tuple(
            assess_objective_contribution(
                contribution,
            )
            for contribution in self.objective_score.contributions
        )