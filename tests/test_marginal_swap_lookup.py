from army import Army
from objective_score import ObjectiveScore
from optimiser_candidate import OptimiserCandidate
from marginal_swap_lookup import (
    build_marginal_swap_lookup,
)


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
            ("a", "d"): 0.70,
        }

        return ObjectiveScore(
            total=scores[profile_ids],
        )


def test_build_marginal_swap_lookup_builds_results_for_each_candidate():
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

    lookup = build_marginal_swap_lookup(
        candidates=(
            candidate_ab,
            candidate_ac,
        ),
        objective=SimpleObjective(),
    )

    assert id(candidate_ab) in lookup
    assert id(candidate_ac) in lookup


def test_build_marginal_swap_lookup_ranks_best_swap_first():
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

    candidate_ad = make_candidate(
        (
            "a",
            "d",
        )
    )

    lookup = build_marginal_swap_lookup(
        candidates=(
            candidate_ab,
            candidate_ad,
            candidate_ac,
        ),
        objective=SimpleObjective(),
    )

    swaps = lookup[
        id(candidate_ab)
    ]

    assert swaps[0].alternative_score == 0.75
    assert swaps[1].alternative_score == 0.70


def test_build_marginal_swap_lookup_returns_empty_tuple_when_no_marginal_alternatives():
    candidate_ab = make_candidate(
        (
            "a",
            "b",
        )
    )

    lookup = build_marginal_swap_lookup(
        candidates=(
            candidate_ab,
        ),
        objective=SimpleObjective(),
    )

    assert lookup[
        id(candidate_ab)
    ] == ()


def test_build_marginal_swap_lookup_returns_empty_dict_for_no_candidates():
    assert build_marginal_swap_lookup(
        candidates=(),
        objective=SimpleObjective(),
    ) == {}