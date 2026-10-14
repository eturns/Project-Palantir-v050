"""DEV-077S-I2-I-A3: verified provider-interface audit (non-scoring).

Grounded against Project-Palantir-v050, commit 51ad0f1.
This module does not import providers, execute simulations, or modify ratings.
It describes contracts and limits that I2-I-B must honour.
"""
from dataclasses import dataclass
from typing import Literal

ProviderStatus = Literal['connected_to_rating', 'diagnostic_only']


@dataclass(frozen=True)
class MechanicalProviderContract:
    metric: str
    module: str
    entrypoint: str
    result_type: str
    status: ProviderStatus
    input_requirements: tuple[str, ...]
    output_evidence: tuple[str, ...]
    unresolved: tuple[str, ...]
    source_commit: str = '51ad0f1'
    missing_evidence: str = 'unavailable_not_zero'
    calibrated_score: bool = False


# The original A2 inventory remains authoritative for the other six metrics.
# Four entries below pin the interfaces that A2 marked for further research.
CONTRACTS = (
    MechanicalProviderContract(
        metric='control',
        module='control_cross_domain_integration',
        entrypoint='build_control_cross_domain_evidence',
        result_type='ControlCrossDomainEvidence',
        status='diagnostic_only',
        input_requirements=('army', 'declared Control casts', 'other declared resource spends'),
        output_evidence=('army Control evidence', 'reconciled Will ledger', 'declared event IDs'),
        unresolved=('no inferred battle outcomes', 'no army-wide calibrated control score',
                    'spell ownership is not a casting opportunity'),
    ),
    MechanicalProviderContract(
        metric='command',
        module='command_army_integration',
        entrypoint='build_army_command_evidence',
        result_type='CommandArmyEvidence',
        status='diagnostic_only',
        input_requirements=('army', 'Heroic Action declarations', 'coverage observations',
                            'explicit other Might expenditure'),
        output_evidence=('fielded actors', 'evaluated declarations',
                         'remaining Might resources', 'recipient coverage'),
        unresolved=('no inferred successful battlefield effects',
                    'no calibrated Command score', 'shared Might cannot be double-spent'),
    ),
    MechanicalProviderContract(
        metric='objective',
        module='objective_scenario_integration',
        entrypoint='build_scenario_objective_evidence',
        result_type='ScenarioObjectiveEvidence',
        status='diagnostic_only',
        input_requirements=('official scenario ID', 'objective position',
                            'observed models', 'verified scenario objective rules'),
        output_evidence=('scenario-aware status', 'endurance report if evidence ready',
                         'presence policy', 'controlling army at scoring when verified'),
        unresolved=('no victory-point calculation', 'capture radius cannot be guessed',
                    'scoring timing cannot be guessed', 'non-hold scenarios need separate handling'),
    ),
    MechanicalProviderContract(
        metric='hero_hunting',
        module='hero_hunting_final_integration',
        entrypoint='validate_hero_hunting_integration',
        result_type='FinalHeroHuntingIntegration',
        status='diagnostic_only',
        input_requirements=('army label', 'real Army', 'optional declared conditional plan'),
        output_evidence=('roster and capability counts', 'unresolved-condition count',
                         'conditional target count', 'coverage consistency'),
        unresolved=('no automatic executable attack selection',
                    'no joint elimination probability', 'no calibrated army-wide score',
                    'target probabilities require exact feasible event sets'),
    ),
)


def get_provider_contract(metric: str) -> MechanicalProviderContract:
    """Return one verified interface; unknown metrics are intentionally rejected."""
    for contract in CONTRACTS:
        if contract.metric == metric:
            return contract
    raise KeyError(metric)


def validate_provider_contracts() -> None:
    """Structural safety gate, not evidence of numerical calibration."""
    expected = ('control', 'command', 'objective', 'hero_hunting')
    if tuple(x.metric for x in CONTRACTS) != expected:
        raise ValueError('A3 contracts must follow canonical four-metric order')
    for contract in CONTRACTS:
        if not all((contract.module, contract.entrypoint, contract.result_type)):
            raise ValueError('Missing provider identity')
        if not contract.input_requirements or not contract.output_evidence or not contract.unresolved:
            raise ValueError('Missing contract evidence or limitations')
        if contract.status != 'diagnostic_only' or contract.calibrated_score:
            raise ValueError('Unapproved scoring connection')
        if contract.missing_evidence != 'unavailable_not_zero':
            raise ValueError('Unknown evidence cannot be interpreted as zero')
        if contract.source_commit != '51ad0f1':
            raise ValueError('Source audit must remain pinned to closure commit')
