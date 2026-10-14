"""DEV-077S-I2-I-A2: inventory contract tests (no scoring changes)."""
import pytest

from metric_constants import METRIC_NAMES
from unified_capability_inventory import (
    get_capability_inventory, get_inventory_entry, validate_capability_inventory,
)


def test_inventory_matches_canonical_metric_names_and_order():
    validate_capability_inventory(METRIC_NAMES)
    assert tuple(entry.metric for entry in get_capability_inventory()) == METRIC_NAMES


@pytest.mark.parametrize('metric', METRIC_NAMES)
def test_every_metric_has_a_traceable_contract(metric):
    entry = get_inventory_entry(metric)
    assert entry.metric == metric
    assert entry.legacy_provider and entry.legacy_unit
    assert entry.mechanical_providers and entry.mechanical_unit
    assert entry.evidence_population
    assert entry.missing_evidence_policy == 'unavailable_not_zero'
    assert entry.calibration_status == 'not_agreed'
    assert entry.scenario_mapping_status == 'not_audited'


def test_inventory_is_immutable():
    from dataclasses import FrozenInstanceError
    with pytest.raises(FrozenInstanceError):
        get_inventory_entry('offence').metric = 'changed'


def test_missing_metric_raises_key_error():
    with pytest.raises(KeyError):
        get_inventory_entry('unknown')


def test_current_production_connections_are_recorded_explicitly():
    assert {e.metric for e in get_capability_inventory() if e.integration_status == 'connected'} == {'offence', 'shooting'}


def test_inventory_does_not_import_or_execute_scoring_engine():
    import inspect
    import unified_capability_inventory
    source = inspect.getsource(unified_capability_inventory)
    assert 'from army_analysis_service import' not in source
    assert 'from army_metric_assessment import' not in source
