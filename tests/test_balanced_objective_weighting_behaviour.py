import balanced_objective

from army import Army
from balanced_objective import BalancedObjective
from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight
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


def test_explicit_preset_weights_can_reverse_candidate_ranking(
    monkeypatch,
):
    combat_army = Army()
    magic_army = Army()

    combat_candidate = OptimiserCandidate(
        army=combat_army,
    )

    magic_candidate = OptimiserCandidate(
        army=magic_army,
    )

    fake_objectives = {
        "board_presence": CandidateAwareObjective(
            {
                id(combat_army): 0.5,
                id(magic_army): 0.5,
            }
        ),
        "battlefield_effects": CandidateAwareObjective(
            {
                id(combat_army): 0.5,
                id(magic_army): 0.5,
            }
        ),
        "combat_capability": CandidateAwareObjective(
            {
                id(combat_army): 0.9,
                id(magic_army): 0.3,
            }
        ),
        "magic": CandidateAwareObjective(
            {
                id(combat_army): 0.3,
                id(magic_army): 0.9,
            }
        ),
        "resource_endurance": CandidateAwareObjective(
            {
                id(combat_army): 0.5,
                id(magic_army): 0.5,
            }
        ),
    }

    monkeypatch.setattr(
        balanced_objective,
        "build_balanced_objectives",
        lambda **kwargs: fake_objectives,
    )

    combat_weighted_preset = ObjectivePreset(
        name="combat_weighted",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=0.10,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=0.10,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=0.50,
            ),
            ObjectiveWeight(
                name="magic",
                weight=0.10,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=0.20,
            ),
        ),
    )

    magic_weighted_preset = ObjectivePreset(
        name="magic_weighted",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=0.10,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=0.10,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=0.10,
            ),
            ObjectiveWeight(
                name="magic",
                weight=0.50,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=0.20,
            ),
        ),
    )

    combat_objective = BalancedObjective(
        preset=combat_weighted_preset,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    magic_objective = BalancedObjective(
        preset=magic_weighted_preset,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    assert (
        combat_objective.evaluate(
            combat_candidate,
        )
        >
        combat_objective.evaluate(
            magic_candidate,
        )
    )

    assert (
        magic_objective.evaluate(
            magic_candidate,
        )
        >
        magic_objective.evaluate(
            combat_candidate,
        )
    )