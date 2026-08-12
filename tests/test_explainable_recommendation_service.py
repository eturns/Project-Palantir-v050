from army import Army
from objective_score import ObjectiveScore
from optimiser_candidate import OptimiserCandidate
from explainable_recommendation_service import (
    build_explainable_recommendations,
)
from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight

class Profile:
    def __init__(
        self,
        profile_id,
    ):
        self.id = profile_id


def make_candidate(
    profile_ids,
):
    army = Army()

    for profile_id in profile_ids:
        army.add_profile(
            Profile(
                profile_id,
            )
        )

    return OptimiserCandidate(
        army=army,
    )


class SimpleObjective:
    def score(
        self,
        candidate,
    ):
        profile_ids = tuple(
            sorted(
                entry.profile.id
                for entry in candidate.army.entries
                for _ in range(entry.quantity)
            )
        )

        scores = {
            ("a", "b"): 0.80,
            ("a", "c"): 0.75,
        }

        return ObjectiveScore(
            total=scores[profile_ids],
        )

    def evaluate(
        self,
        candidate,
    ):
        return self.score(
            candidate,
        ).total


def test_build_explainable_recommendations_ranks_candidates():
    candidate_ab = make_candidate(
        (
            "a",
            "b",
        )
    )

    candidate_ac = make_candidate(
        (
            "a",
            "c",
        )
    )

    recommendations = build_explainable_recommendations(
        candidates=(
            candidate_ac,
            candidate_ab,
        ),
        objective=SimpleObjective(),
    )

    assert recommendations[0].candidate == candidate_ab
    assert recommendations[0].rank == 1

    assert recommendations[1].candidate == candidate_ac
    assert recommendations[1].rank == 2


def test_build_explainable_recommendations_preserves_transparent_scores():
    candidate_ab = make_candidate(
        (
            "a",
            "b",
        )
    )

    recommendations = build_explainable_recommendations(
        candidates=(
            candidate_ab,
        ),
        objective=SimpleObjective(),
    )

    assert recommendations[0].objective_score == ObjectiveScore(
        total=0.80,
    )


def test_build_explainable_recommendations_attaches_marginal_swaps():
    candidate_ab = make_candidate(
        (
            "a",
            "b",
        )
    )

    candidate_ac = make_candidate(
        (
            "a",
            "c",
        )
    )

    recommendations = build_explainable_recommendations(
        candidates=(
            candidate_ab,
            candidate_ac,
        ),
        objective=SimpleObjective(),
    )

    assert len(
        recommendations[0].marginal_swaps
    ) == 1

    assert (
        recommendations[0]
        .marginal_swaps[0]
        .alternative_score
        == 0.75
    )


def test_build_explainable_recommendations_returns_empty_tuple_for_no_candidates():
    assert build_explainable_recommendations(
        candidates=(),
        objective=SimpleObjective(),
    ) == ()

class RejectCandidateConstraint:
    def validate(
        self,
        candidate,
    ):
        profile_ids = tuple(
            sorted(
                entry.profile.id
                for entry in candidate.army.entries
                for _ in range(entry.quantity)
            )
        )

        if profile_ids == (
            "a",
            "c",
        ):
            return [
                "Candidate is not permitted.",
            ]

        return []


def test_build_explainable_recommendations_preserves_constraint_errors():
    candidate_ab = make_candidate(
        (
            "a",
            "b",
        )
    )

    candidate_ac = make_candidate(
        (
            "a",
            "c",
        )
    )

    recommendations = build_explainable_recommendations(
        candidates=(
            candidate_ab,
            candidate_ac,
        ),
        objective=SimpleObjective(),
        constraints=(
            RejectCandidateConstraint(),
        ),
    )

    recommendation_by_candidate = {
        recommendation.candidate: recommendation
        for recommendation in recommendations
    }

    assert (
        recommendation_by_candidate[
            candidate_ab
        ].constraint_errors
        == ()
    )

    assert (
        recommendation_by_candidate[
            candidate_ac
        ].constraint_errors
        == (
            "Candidate is not permitted.",
        )
    )

class PresetDrivenObjective:
    def __init__(
        self,
        *,
        preset,
    ):
        self.preset = preset

    def score(
        self,
        candidate,
    ):
        profile_ids = tuple(
            sorted(
                entry.profile.id
                for entry in candidate.army.entries
                for _ in range(entry.quantity)
            )
        )

        magic_weight = next(
            weight.weight
            for weight in self.preset.weights
            if weight.name == "magic"
        )

        if profile_ids == (
            "candidate_a",
        ):
            total = 0.80 - magic_weight

        elif profile_ids == (
            "candidate_b",
        ):
            total = 0.35 + magic_weight

        else:
            raise AssertionError(
                f"Unexpected candidate: {profile_ids}"
            )

        return ObjectiveScore(
            total=total,
        )

    def evaluate(
        self,
        candidate,
    ):
        return self.score(
            candidate,
        ).total


def make_balanced_preset():
    return ObjectivePreset(
        name="balanced",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="magic",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=0.20,
            ),
        ),
    )


def build_preset_objective(
    preset,
):
    return PresetDrivenObjective(
        preset=preset,
    )


def test_build_explainable_recommendations_attaches_sensitivity_stability():
    candidate_a = make_candidate(
        (
            "candidate_a",
        )
    )

    candidate_b = make_candidate(
        (
            "candidate_b",
        )
    )

    preset = make_balanced_preset()

    recommendations = build_explainable_recommendations(
        candidates=(
            candidate_a,
            candidate_b,
        ),
        objective=build_preset_objective(
            preset,
        ),
        sensitivity_preset=preset,
        sensitivity_objective_factory=build_preset_objective,
        sensitivity_delta=0.10,
    )

    assert recommendations[0].candidate == candidate_a

    stability = (
        recommendations[0]
        .sensitivity_stability
    )

    assert stability is not None
    assert stability.candidate_key == "candidate_a:1"
    assert stability.variant_count == 10
    assert stability.rank_one_count < 10
    assert stability.worst_rank == 2
    assert stability.fully_stable is False