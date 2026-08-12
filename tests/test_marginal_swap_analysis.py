from army import Army
from marginal_swap_analysis import analyse_marginal_swaps
from marginal_swap_result import (
    MarginalCapabilityDelta,
    MarginalSwapResult,
)
from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from optimiser_candidate import OptimiserCandidate
from profile_swap import ProfileSwap
from profiles import Profile


def make_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=80,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def make_candidate(
    entries: tuple[tuple[Profile, int], ...],
) -> OptimiserCandidate:
    army = Army()

    for profile, quantity in entries:
        army.add_profile(
            profile,
            quantity=quantity,
        )

    return OptimiserCandidate(
        army=army,
    )


class TransparentObjective:
    def __init__(
        self,
        scores_by_profiles,
    ):
        self.scores_by_profiles = scores_by_profiles

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

        return self.scores_by_profiles[
            profile_ids
        ]


def test_analyse_marginal_swaps_builds_scored_swap_result():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")
    profile_c = make_profile("nazgul_c")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_c, 1),
        )
    )

    objective = TransparentObjective(
        {
            ("nazgul_a", "nazgul_b"): ObjectiveScore(
                total=0.60,
                contributions=(
                    ObjectiveContribution(
                        name="combat_capability",
                        value=0.60,
                    ),
                ),
            ),
            ("nazgul_a", "nazgul_c"): ObjectiveScore(
                total=0.68,
                contributions=(
                    ObjectiveContribution(
                        name="combat_capability",
                        value=0.72,
                    ),
                ),
            ),
        }
    )

    results = analyse_marginal_swaps(
        original=original,
        candidates=(
            alternative,
        ),
        objective=objective,
    )

    assert results == (
        MarginalSwapResult(
            swap=ProfileSwap(
                removed_profile_id="nazgul_b",
                added_profile_id="nazgul_c",
            ),
            original_score=0.60,
            alternative_score=0.68,
            capability_deltas=(
                MarginalCapabilityDelta(
                    name="combat_capability",
                    original_value=0.60,
                    alternative_value=0.72,
                ),
            ),
        ),
    )


def test_analyse_marginal_swaps_ignores_non_marginal_candidates():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")
    profile_c = make_profile("nazgul_c")
    profile_d = make_profile("nazgul_d")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    unrelated = make_candidate(
        (
            (profile_c, 1),
            (profile_d, 1),
        )
    )

    objective = TransparentObjective(
        {
            ("nazgul_a", "nazgul_b"): ObjectiveScore(
                total=0.60,
            ),
        }
    )

    assert analyse_marginal_swaps(
        original=original,
        candidates=(
            unrelated,
        ),
        objective=objective,
    ) == ()


def test_analyse_marginal_swaps_preserves_candidate_pool_order():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")
    profile_c = make_profile("nazgul_c")
    profile_d = make_profile("nazgul_d")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    first_alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_c, 1),
        )
    )

    second_alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_d, 1),
        )
    )

    objective = TransparentObjective(
        {
            ("nazgul_a", "nazgul_b"): ObjectiveScore(
                total=0.60,
            ),
            ("nazgul_a", "nazgul_c"): ObjectiveScore(
                total=0.65,
            ),
            ("nazgul_a", "nazgul_d"): ObjectiveScore(
                total=0.70,
            ),
        }
    )

    results = analyse_marginal_swaps(
        original=original,
        candidates=(
            first_alternative,
            second_alternative,
        ),
        objective=objective,
    )

    assert results[0].swap.added_profile_id == "nazgul_c"
    assert results[1].swap.added_profile_id == "nazgul_d"


def test_analyse_marginal_swaps_returns_empty_tuple_when_none_exist():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    objective = TransparentObjective(
        {
            ("nazgul_a", "nazgul_b"): ObjectiveScore(
                total=0.60,
            ),
        }
    )

    assert analyse_marginal_swaps(
        original=original,
        candidates=(),
        objective=objective,
    ) == ()

class RejectProfileConstraint:
    def __init__(
        self,
        rejected_profile_id,
    ):
        self.rejected_profile_id = rejected_profile_id

    def validate(
        self,
        candidate,
    ):
        profile_ids = {
            entry.profile.id
            for entry in candidate.army.entries
        }

        if self.rejected_profile_id in profile_ids:
            return (
                f"{self.rejected_profile_id} is not permitted.",
            )

        return ()


def test_analyse_marginal_swaps_excludes_alternatives_that_fail_constraints():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")
    profile_c = make_profile("nazgul_c")
    profile_d = make_profile("nazgul_d")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    permitted_alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_c, 1),
        )
    )

    rejected_alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_d, 1),
        )
    )

    objective = TransparentObjective(
        {
            ("nazgul_a", "nazgul_b"): ObjectiveScore(
                total=0.60,
            ),
            ("nazgul_a", "nazgul_c"): ObjectiveScore(
                total=0.65,
            ),
            ("nazgul_a", "nazgul_d"): ObjectiveScore(
                total=0.70,
            ),
        }
    )

    results = analyse_marginal_swaps(
        original=original,
        candidates=(
            permitted_alternative,
            rejected_alternative,
        ),
        objective=objective,
        constraints=(
            RejectProfileConstraint(
                "nazgul_d",
            ),
        ),
    )

    assert len(results) == 1
    assert results[0].swap.added_profile_id == "nazgul_c"