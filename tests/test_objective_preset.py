import pytest

from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight


def test_objective_preset_stores_named_weights():
    preset = ObjectivePreset(
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

    assert preset.name == "balanced"
    assert len(preset.weights) == 5


def test_objective_preset_requires_weights_to_sum_to_one():
    with pytest.raises(ValueError):
        ObjectivePreset(
            name="invalid",
            weights=(
                ObjectiveWeight(
                    name="board_presence",
                    weight=0.40,
                ),
                ObjectiveWeight(
                    name="combat_capability",
                    weight=0.40,
                ),
            ),
        )


def test_objective_preset_rejects_duplicate_component_names():
    with pytest.raises(ValueError):
        ObjectivePreset(
            name="invalid",
            weights=(
                ObjectiveWeight(
                    name="combat_capability",
                    weight=0.50,
                ),
                ObjectiveWeight(
                    name="combat_capability",
                    weight=0.50,
                ),
            ),
        )