from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from recommendation_capabilities import (
    find_strongest_contributions,
    find_weakest_contributions,
)


def test_find_strongest_contributions_returns_highest_scoring_contribution():
    score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.70,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.80,
            ),
            ObjectiveContribution(
                name="magic",
                value=0.40,
            ),
        ),
    )

    assert find_strongest_contributions(
        score,
    ) == (
        ObjectiveContribution(
            name="combat_capability",
            value=0.80,
        ),
    )


def test_find_weakest_contributions_returns_lowest_scoring_contribution():
    score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.70,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.80,
            ),
            ObjectiveContribution(
                name="magic",
                value=0.40,
            ),
        ),
    )

    assert find_weakest_contributions(
        score,
    ) == (
        ObjectiveContribution(
            name="magic",
            value=0.40,
        ),
    )


def test_strongest_contributions_preserve_ties():
    score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.80,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.80,
            ),
            ObjectiveContribution(
                name="magic",
                value=0.40,
            ),
        ),
    )

    assert find_strongest_contributions(
        score,
    ) == (
        ObjectiveContribution(
            name="board_presence",
            value=0.80,
        ),
        ObjectiveContribution(
            name="combat_capability",
            value=0.80,
        ),
    )


def test_weakest_contributions_preserve_ties():
    score = ObjectiveScore(
        total=0.60,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.80,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.40,
            ),
            ObjectiveContribution(
                name="magic",
                value=0.40,
            ),
        ),
    )

    assert find_weakest_contributions(
        score,
    ) == (
        ObjectiveContribution(
            name="combat_capability",
            value=0.40,
        ),
        ObjectiveContribution(
            name="magic",
            value=0.40,
        ),
    )


def test_empty_contributions_return_empty_strengths_and_weaknesses():
    score = ObjectiveScore(
        total=0.60,
    )

    assert find_strongest_contributions(
        score,
    ) == ()

    assert find_weakest_contributions(
        score,
    ) == ()