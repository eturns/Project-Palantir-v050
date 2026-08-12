import balanced_objective

from army import Army
from balanced_objective import BalancedObjective
from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)
from optimiser_candidate import OptimiserCandidate


class CandidateAwareObjective:
    def __init__(
        self,
        scores_by_army,
    ):
        self.scores_by_army = scores_by_army

    def evaluate(
        self,
        candidate,
    ):
        return self.scores_by_army[
            id(candidate.army)
        ]


def test_balanced_objective_prefers_broad_capability_over_specialisation(
    monkeypatch,
):
    balanced_army = Army()
    specialist_army = Army()

    balanced_candidate = OptimiserCandidate(
        army=balanced_army,
    )

    specialist_candidate = OptimiserCandidate(
        army=specialist_army,
    )

    balanced_scores = (
        0.60,
        0.60,
        0.60,
        0.60,
        0.60,
    )

    specialist_scores = (
        0.80,
        0.80,
        0.80,
        0.20,
        0.20,
    )

    objective_names = (
        "board_presence",
        "battlefield_effects",
        "combat_capability",
        "magic",
        "resource_endurance",
    )

    fake_objectives = {}

    for name, balanced_score, specialist_score in zip(
        objective_names,
        balanced_scores,
        specialist_scores,
    ):
        fake_objectives[name] = CandidateAwareObjective(
            {
                id(balanced_army): balanced_score,
                id(specialist_army): specialist_score,
            }
        )

    monkeypatch.setattr(
        balanced_objective,
        "build_balanced_objectives",
        lambda **kwargs: fake_objectives,
    )

    objective = BalancedObjective(
        preset=BALANCED_OBJECTIVE_PRESET,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    balanced_result = objective.evaluate(
        balanced_candidate,
    )

    specialist_result = objective.evaluate(
        specialist_candidate,
    )

    assert balanced_result > specialist_result