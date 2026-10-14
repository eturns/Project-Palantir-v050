"""DEV-077S-I2-I-A3: contract-only regression tests."""
import pytest
from unified_capability_provider_audit import (
    CONTRACTS, get_provider_contract, validate_provider_contracts,
)


def test_provider_registry_validates():
    validate_provider_contracts()


@pytest.mark.parametrize('metric,module,entrypoint', [
    ('control', 'control_cross_domain_integration', 'build_control_cross_domain_evidence'),
    ('command', 'command_army_integration', 'build_army_command_evidence'),
    ('objective', 'objective_scenario_integration', 'build_scenario_objective_evidence'),
    ('hero_hunting', 'hero_hunting_final_integration', 'validate_hero_hunting_integration'),
])
def test_verified_provider_identity(metric, module, entrypoint):
    contract = get_provider_contract(metric)
    assert (contract.module, contract.entrypoint) == (module, entrypoint)


@pytest.mark.parametrize('contract', CONTRACTS, ids=lambda c: c.metric)
def test_no_scoring_or_zero_substitution(contract):
    assert contract.status == 'diagnostic_only'
    assert contract.calibrated_score is False
    assert contract.missing_evidence == 'unavailable_not_zero'
    assert contract.unresolved


def test_unknown_metric_rejected():
    with pytest.raises(KeyError):
        get_provider_contract('shooting')


def test_source_commit_pinned():
    assert {c.source_commit for c in CONTRACTS} == {'51ad0f1'}


def test_objective_needs_verified_rules():
    contract = get_provider_contract('objective')
    assert 'verified scenario objective rules' in contract.input_requirements
    assert 'no victory-point calculation' in contract.unresolved


def test_hero_hunting_does_not_sum_target_probabilities():
    contract = get_provider_contract('hero_hunting')
    assert 'no joint elimination probability' in contract.unresolved
