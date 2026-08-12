from objective_component import MetricObjectiveComponent
from weighted_objective import WeightedObjective


def test_weighted_objective_combines_component_contributions():
    objective = WeightedObjective(
        components=(
            MetricObjectiveComponent(
                name="magic",
                minimum=0.0,
                maximum=10.0,
                weight=0.5,
            ),
            MetricObjectiveComponent(
                name="control",
                minimum=0.0,
                maximum=20.0,
                weight=0.5,
            ),
        ),
    )

    score = objective.evaluate(
        values={
            "magic": 5.0,
            "control": 10.0,
        }
    )

    assert score.total == 0.5

    assert tuple(
        (
            contribution.name,
            contribution.value,
        )
        for contribution in score.contributions
    ) == (
        ("magic", 0.25),
        ("control", 0.25),
    )