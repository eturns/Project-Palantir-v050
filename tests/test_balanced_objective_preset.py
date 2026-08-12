import pytest

from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)


def test_balanced_objective_preset_has_explicit_equal_weights():
    weights_by_name = {
        weight.name: weight.weight
        for weight in BALANCED_OBJECTIVE_PRESET.weights
    }

    assert weights_by_name == {
        "board_presence": pytest.approx(0.20),
        "battlefield_effects": pytest.approx(0.20),
        "combat_capability": pytest.approx(0.20),
        "magic": pytest.approx(0.20),
        "resource_endurance": pytest.approx(0.20),
    }


def test_balanced_objective_preset_is_named_balanced():
    assert BALANCED_OBJECTIVE_PRESET.name == "balanced"