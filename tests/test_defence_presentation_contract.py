"""Compatibility-safe tests for the two-measure Defence dashboard contract."""
from dataclasses import FrozenInstanceError
import pytest

from defence_presentation_contract import from_mechanical_diagnostics


def sample():
    return {
        "combat_density": 2.9270251837875314,
        "combat_survival": 0.5246129752480729,
        "recovery_density": 999.0,
        "recovery_presence": 1.0,
        "engagements": 3,
    }


def test_uses_existing_combat_only_values_verbatim():
    presentation = from_mechanical_diagnostics(sample())
    assert presentation.army_survival_density.value == sample()["combat_density"]
    assert presentation.per_model_resilience.value == sample()["combat_survival"]


def test_labels_are_distinct_and_meaningful():
    presentation = from_mechanical_diagnostics(sample())
    assert presentation.army_survival_density.label == "Army Survival Density"
    assert presentation.per_model_resilience.label == "Per-Model Resilience"
    assert presentation.army_survival_density.unit != presentation.per_model_resilience.unit


def test_resurrection_is_not_substituted_for_combat_results():
    presentation = from_mechanical_diagnostics(sample())
    assert presentation.army_survival_density.value != 999.0
    assert presentation.per_model_resilience.value != 1.0


def test_values_are_explicitly_not_calibrated():
    presentation = from_mechanical_diagnostics(sample())
    assert not presentation.army_survival_density.calibrated
    assert not presentation.per_model_resilience.calibrated
    assert not presentation.production_score_changed


@pytest.mark.parametrize("value", [-1.0, float("inf"), float("nan")])
def test_bad_density_rejected(value):
    data = sample()
    data["combat_density"] = value
    with pytest.raises(ValueError):
        from_mechanical_diagnostics(data)


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan")])
def test_bad_resilience_rejected(value):
    data = sample()
    data["combat_survival"] = value
    with pytest.raises(ValueError):
        from_mechanical_diagnostics(data)


def test_missing_original_mechanical_fields_fail_loudly():
    with pytest.raises(KeyError):
        from_mechanical_diagnostics({"combat_density": 1.0, "engagements": 3})


def test_presentation_is_immutable():
    presentation = from_mechanical_diagnostics(sample())
    with pytest.raises(FrozenInstanceError):
        presentation.engagements = 4


def test_bool_engagements_rejected():
    data = sample()
    data["engagements"] = True
    with pytest.raises(ValueError):
        from_mechanical_diagnostics(data)
