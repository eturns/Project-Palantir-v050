from marginal_swap_ranking import (
    rank_marginal_swaps,
)
from marginal_swap_result import MarginalSwapResult
from profile_swap import ProfileSwap


def make_result(
    added_profile_id: str,
    *,
    original_score: float,
    alternative_score: float,
) -> MarginalSwapResult:
    return MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id=added_profile_id,
        ),
        original_score=original_score,
        alternative_score=alternative_score,
    )


def test_rank_marginal_swaps_orders_highest_total_delta_first():
    small_improvement = make_result(
        "nazgul_b",
        original_score=0.60,
        alternative_score=0.62,
    )

    large_improvement = make_result(
        "nazgul_c",
        original_score=0.60,
        alternative_score=0.68,
    )

    decline = make_result(
        "nazgul_d",
        original_score=0.60,
        alternative_score=0.55,
    )

    ranked = rank_marginal_swaps(
        (
            small_improvement,
            decline,
            large_improvement,
        )
    )

    assert ranked == (
        large_improvement,
        small_improvement,
        decline,
    )


def test_rank_marginal_swaps_preserves_existing_order_for_equal_deltas():
    first = make_result(
        "nazgul_b",
        original_score=0.60,
        alternative_score=0.65,
    )

    second = make_result(
        "nazgul_c",
        original_score=0.60,
        alternative_score=0.65,
    )

    ranked = rank_marginal_swaps(
        (
            first,
            second,
        )
    )

    assert ranked == (
        first,
        second,
    )


def test_rank_marginal_swaps_returns_empty_tuple_for_empty_input():
    assert rank_marginal_swaps(
        (),
    ) == ()