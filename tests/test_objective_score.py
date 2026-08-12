from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)


def test_objective_score_stores_total_and_named_contributions():
    score = ObjectiveScore(
        total=78.4,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=41.2,
            ),
            ObjectiveContribution(
                name="magic",
                value=37.2,
            ),
        ),
    )

    assert score.total == 78.4

    assert score.contributions == (
        ObjectiveContribution(
            name="board_presence",
            value=41.2,
        ),
        ObjectiveContribution(
            name="magic",
            value=37.2,
        ),
    )