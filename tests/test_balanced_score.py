import pytest

from balanced_score import calculate_balanced_score


def test_balanced_score_rewards_consistent_capability():
    score = calculate_balanced_score(
        component_scores=(
            0.6,
            0.6,
            0.6,
            0.6,
        ),
    )

    assert score == pytest.approx(
        0.6,
    )


def test_balanced_score_penalises_major_weaknesses():
    score = calculate_balanced_score(
        component_scores=(
            0.8,
            0.8,
            0.2,
            0.2,
        ),
    )

    assert score == pytest.approx(
        0.425,
    )


def test_balanced_score_rejects_empty_components():
    with pytest.raises(ValueError):
        calculate_balanced_score(
            component_scores=(),
        )