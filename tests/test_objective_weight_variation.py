import pytest

from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight
from objective_weight_variation import (
    vary_objective_weight,
)


def make_balanced_preset() -> ObjectivePreset:
    return ObjectivePreset(
        name="balanced",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="magic",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=0.20,
            ),
        ),
    )


def test_vary_objective_weight_sets_requested_weight():
    preset = make_balanced_preset()

    variant = vary_objective_weight(
        preset=preset,
        capability="magic",
        variant_weight=0.25,
    )

    weights_by_name = {
        weight.name: weight.weight
        for weight in variant.weights
    }

    assert weights_by_name["magic"] == pytest.approx(
        0.25,
    )


def test_vary_objective_weight_rescales_other_weights_proportionally():
    preset = make_balanced_preset()

    variant = vary_objective_weight(
        preset=preset,
        capability="magic",
        variant_weight=0.25,
    )

    weights_by_name = {
        weight.name: weight.weight
        for weight in variant.weights
    }

    assert weights_by_name["board_presence"] == pytest.approx(
        0.1875,
    )
    assert weights_by_name["battlefield_effects"] == pytest.approx(
        0.1875,
    )
    assert weights_by_name["combat_capability"] == pytest.approx(
        0.1875,
    )
    assert weights_by_name["resource_endurance"] == pytest.approx(
        0.1875,
    )


def test_vary_objective_weight_can_reduce_requested_weight():
    preset = make_balanced_preset()

    variant = vary_objective_weight(
        preset=preset,
        capability="magic",
        variant_weight=0.15,
    )

    weights_by_name = {
        weight.name: weight.weight
        for weight in variant.weights
    }

    assert weights_by_name["magic"] == pytest.approx(
        0.15,
    )

    assert weights_by_name["board_presence"] == pytest.approx(
        0.2125,
    )


def test_vary_objective_weight_preserves_weight_order():
    preset = make_balanced_preset()

    variant = vary_objective_weight(
        preset=preset,
        capability="magic",
        variant_weight=0.25,
    )

    assert tuple(
        weight.name
        for weight in variant.weights
    ) == tuple(
        weight.name
        for weight in preset.weights
    )


def test_vary_objective_weight_returns_weights_summing_to_one():
    preset = make_balanced_preset()

    variant = vary_objective_weight(
        preset=preset,
        capability="magic",
        variant_weight=0.25,
    )

    assert sum(
        weight.weight
        for weight in variant.weights
    ) == pytest.approx(
        1.0,
    )


def test_vary_objective_weight_does_not_mutate_baseline_preset():
    preset = make_balanced_preset()

    vary_objective_weight(
        preset=preset,
        capability="magic",
        variant_weight=0.25,
    )

    assert tuple(
        weight.weight
        for weight in preset.weights
    ) == (
        0.20,
        0.20,
        0.20,
        0.20,
        0.20,
    )


def test_vary_objective_weight_rejects_unknown_capability():
    preset = make_balanced_preset()

    with pytest.raises(ValueError):
        vary_objective_weight(
            preset=preset,
            capability="unknown",
            variant_weight=0.25,
        )


@pytest.mark.parametrize(
    "variant_weight",
    (
        -0.01,
        1.01,
    ),
)
def test_vary_objective_weight_rejects_weight_outside_zero_to_one(
    variant_weight,
):
    preset = make_balanced_preset()

    with pytest.raises(ValueError):
        vary_objective_weight(
            preset=preset,
            capability="magic",
            variant_weight=variant_weight,
        )