import pytest

from objective_weight import ObjectiveWeight


def test_objective_weight_stores_named_weight():
    weight = ObjectiveWeight(
        name="combat_capability",
        weight=0.25,
    )

    assert weight.name == "combat_capability"
    assert weight.weight == pytest.approx(0.25)


def test_objective_weight_rejects_negative_weight():
    with pytest.raises(ValueError):
        ObjectiveWeight(
            name="combat_capability",
            weight=-0.1,
        )