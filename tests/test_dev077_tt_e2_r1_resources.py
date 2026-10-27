"""DEV-077-TT-E2-R1: production ConfiguredProfile resource lookup."""
from types import SimpleNamespace
import pytest
from three_trolls_d4e_analysis import _starting_resource


@pytest.mark.parametrize("resource,value", [("might", 2), ("will", 3), ("fate", 1)])
def test_production_configured_profile_uses_canonical_base_resource(resource, value):
    configured = SimpleNamespace(profile=SimpleNamespace(might=2, will=3, fate=1))
    assert _starting_resource(configured, resource) == value


@pytest.mark.parametrize("resource,value", [("might", 2), ("will", 3), ("fate", 1)])
def test_e1_adapter_remains_compatible(resource, value):
    configured = SimpleNamespace(get_attribute=lambda key: {"might": 2, "will": 3, "fate": 1}[key])
    assert _starting_resource(configured, resource) == value


def test_invalid_resource_type_rejected():
    with pytest.raises(ValueError):
        _starting_resource(SimpleNamespace(profile=SimpleNamespace(might=True)), "might")


def test_missing_interface_rejected():
    with pytest.raises(TypeError):
        _starting_resource(SimpleNamespace(), "might")
