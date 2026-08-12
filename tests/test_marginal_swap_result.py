import pytest

from marginal_swap_result import (
    MarginalCapabilityDelta,
    MarginalSwapResult,
)
from profile_swap import ProfileSwap


def test_marginal_swap_result_stores_swap_and_total_scores():
    result = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id="nazgul_b",
        ),
        original_score=0.60,
        alternative_score=0.65,
    )

    assert result.swap == ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    assert result.original_score == 0.60
    assert result.alternative_score == 0.65


def test_marginal_swap_result_calculates_positive_total_delta():
    result = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id="nazgul_b",
        ),
        original_score=0.60,
        alternative_score=0.65,
    )

    assert result.total_delta == pytest.approx(
        0.05,
    )


def test_marginal_swap_result_calculates_negative_total_delta():
    result = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id="nazgul_b",
        ),
        original_score=0.70,
        alternative_score=0.62,
    )

    assert result.total_delta == pytest.approx(
        -0.08,
    )


def test_marginal_capability_delta_stores_name_and_values():
    delta = MarginalCapabilityDelta(
        name="combat_capability",
        original_value=0.60,
        alternative_value=0.72,
    )

    assert delta.name == "combat_capability"
    assert delta.original_value == 0.60
    assert delta.alternative_value == 0.72


def test_marginal_capability_delta_calculates_delta():
    delta = MarginalCapabilityDelta(
        name="combat_capability",
        original_value=0.60,
        alternative_value=0.72,
    )

    assert delta.delta == pytest.approx(
        0.12,
    )


def test_marginal_swap_result_preserves_capability_deltas():
    capability_deltas = (
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

    result = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id="nazgul_b",
        ),
        original_score=0.60,
        alternative_score=0.65,
        capability_deltas=capability_deltas,
    )

    assert result.capability_deltas == capability_deltas


def test_marginal_swap_result_is_immutable():
    result = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id="nazgul_b",
        ),
        original_score=0.60,
        alternative_score=0.65,
    )

    with pytest.raises(Exception):
        result.original_score = 0.50