import pytest

from marginal_swap_builder import (
    build_marginal_swap_result,
)
from marginal_swap_result import (
    MarginalCapabilityDelta,
    MarginalSwapResult,
)
from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from profile_swap import ProfileSwap


def test_build_marginal_swap_result_preserves_total_scores():
    swap = ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    original_score = ObjectiveScore(
        total=0.60,
    )

    alternative_score = ObjectiveScore(
        total=0.65,
    )

    result = build_marginal_swap_result(
        swap=swap,
        original_score=original_score,
        alternative_score=alternative_score,
    )

    assert result.original_score == 0.60
    assert result.alternative_score == 0.65
    assert result.total_delta == pytest.approx(
        0.05,
    )


def test_build_marginal_swap_result_builds_capability_deltas():
    swap = ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    original_score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.70,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.60,
            ),
        ),
    )

    alternative_score = ObjectiveScore(
        total=0.65,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.65,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.72,
            ),
        ),
    )

    result = build_marginal_swap_result(
        swap=swap,
        original_score=original_score,
        alternative_score=alternative_score,
    )

    assert result == MarginalSwapResult(
        swap=swap,
        original_score=0.60,
        alternative_score=0.65,
        capability_deltas=(
            MarginalCapabilityDelta(
                name="board_presence",
                original_value=0.70,
                alternative_value=0.65,
            ),
            MarginalCapabilityDelta(
                name="combat_capability",
                original_value=0.60,
                alternative_value=0.72,
            ),
        ),
    )


def test_build_marginal_swap_result_matches_capabilities_by_name():
    swap = ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    original_score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.70,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.60,
            ),
        ),
    )

    alternative_score = ObjectiveScore(
        total=0.65,
        contributions=(
            ObjectiveContribution(
                name="combat_capability",
                value=0.72,
            ),
            ObjectiveContribution(
                name="board_presence",
                value=0.65,
            ),
        ),
    )

    result = build_marginal_swap_result(
        swap=swap,
        original_score=original_score,
        alternative_score=alternative_score,
    )

    assert result.capability_deltas == (
        MarginalCapabilityDelta(
            name="board_presence",
            original_value=0.70,
            alternative_value=0.65,
        ),
        MarginalCapabilityDelta(
            name="combat_capability",
            original_value=0.60,
            alternative_value=0.72,
        ),
    )


def test_build_marginal_swap_result_rejects_different_capability_sets():
    swap = ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    original_score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.70,
            ),
        ),
    )

    alternative_score = ObjectiveScore(
        total=0.65,
        contributions=(
            ObjectiveContribution(
                name="magic",
                value=0.70,
            ),
        ),
    )

    with pytest.raises(ValueError):
        build_marginal_swap_result(
            swap=swap,
            original_score=original_score,
            alternative_score=alternative_score,
        )