from objective_component import MetricObjectiveComponent


def test_metric_objective_component_scores_normalised_weighted_value():
    component = MetricObjectiveComponent(
        name="magic",
        minimum=0.0,
        maximum=10.0,
        weight=0.4,
    )

    contribution = component.evaluate(
        value=5.0
    )

    assert contribution.name == "magic"
    assert contribution.value == 0.2