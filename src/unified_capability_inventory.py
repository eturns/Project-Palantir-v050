"""DEV-077S-I2-I-A2: declarative, non-scoring inventory of capability providers.

This module makes no numerical calibration decisions and never imports scoring
providers. Provider symbols are source-audit pointers, not runtime dependencies.
"""
from dataclasses import dataclass
from typing import Literal

METRIC_NAMES = (
    'offence', 'defence', 'mobility', 'magic', 'shooting',
    'courage', 'control', 'command', 'objective', 'hero_hunting',
)

EvidenceStatus = Literal['connected', 'diagnostic', 'research']
MissingPolicy = Literal['unavailable_not_zero']


@dataclass(frozen=True)
class CapabilityInventoryEntry:
    metric: str
    legacy_provider: str
    legacy_unit: str
    mechanical_providers: tuple[str, ...]
    mechanical_unit: str
    integration_status: EvidenceStatus
    evidence_population: str
    dependencies: tuple[str, ...]
    missing_evidence_policy: MissingPolicy = 'unavailable_not_zero'
    calibration_status: str = 'not_agreed'
    scenario_mapping_status: str = 'not_audited'
    notes: str = ''


_SHARED_LEGACY = 'profile_metrics.calculate_profile_metrics -> army_metrics.calculate_army_metrics -> army_metric_densities.calculate_army_metric_densities'
_INVENTORY = (
    CapabilityInventoryEntry('offence', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('army_offence_capability.calculate_army_offensive_output_density',),
        'mechanical offensive output density (benchmark-specific)', 'connected',
        'configured army against chosen combat benchmark', ('defence', 'hero_hunting'),
        notes='Mechanical value feeds army_metric_assessment; threshold calibration requires audit.'),
    CapabilityInventoryEntry('defence', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('mechanical_defence_diagnostics.calculate_mechanical_defence_diagnostics',),
        'diagnostic survivability measures (inspect field-level units)', 'diagnostic',
        'configured army and benchmark attacker assumptions', ('courage',),
        notes='Service exposes mechanical_defence separately; not yet scored.'),
    CapabilityInventoryEntry('mobility', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('mobility_integration_contract.build_mobility_integration_contract',),
        'contextual movement and terrain diagnostics', 'diagnostic',
        'configured models with terrain and base-size assumptions', ('objective',),
        notes='Service exposes mechanical_mobility separately; not yet scored.'),
    CapabilityInventoryEntry('magic', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('mechanical_magic_army_contract.build_army_magic_contract',
         'mechanical_magic_completeness.audit_army_magic_completeness'),
        'casting/resource/repertoire evidence (not a calibrated score)', 'diagnostic',
        'eligible casters, spells and army-level casting resources', ('control', 'hero_hunting'),
        notes='Mechanical contract is guarded by completeness; absent evidence must not become zero.'),
    CapabilityInventoryEntry('shooting', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('army_shooting_capability.calculate_army_shooting_output_density',
         'objective_normalisation.normalise_shooting_output_density'),
        'normalised shooting output from benchmark-dependent density', 'connected',
        'configured ranged models versus benchmark defender', ('offence', 'hero_hunting'),
        notes='Mechanical value feeds army_metric_assessment; avoid repeating ranged kills in offence.'),
    CapabilityInventoryEntry('courage', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('courage_integration_contract.build_courage_integration_contract',),
        'conditional courage-test probability and related evidence', 'diagnostic',
        'configured army in a specified test and opponent context', ('control',),
        notes='Service exposes mechanical_courage separately; dashboard/scenario scores are not populated.'),
    CapabilityInventoryEntry('control', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('control_cross_domain_integration',),
        'effect-state and Will-ledger evidence; raw output contract to verify', 'research',
        'effects, legal transitions, recipients and expiry', ('magic', 'courage'),
        notes='H1 evidence exists, but an army-to-dashboard aggregation interface is not yet established.'),
    CapabilityInventoryEntry('command', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('command heroic-action integration (H2; exact exported symbol to audit)',),
        'legal heroic-action, coverage and Might-ledger evidence', 'research',
        'heroes, recipients and available Might', ('mobility', 'offence'),
        notes='H2 evidence exists; pin exact source symbol before runtime wiring.'),
    CapabilityInventoryEntry('objective', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('objective position/presence and Dominant integration (H3; exact symbol to audit)',),
        'scenario-conditioned presence, reachability and contest evidence', 'research',
        'fielded models and scenario-specific objective conditions', ('mobility', 'defence', 'command'),
        notes='Official victory-point scoring and capture-timing coverage is not exhaustive.'),
    CapabilityInventoryEntry('hero_hunting', _SHARED_LEGACY, 'legacy contributions per 100 army points',
        ('hero_hunting_final_integration', 'hero_hunting_real_evidence_report'),
        'target-specific hero elimination probability and threat evidence', 'research',
        'attacker resources, named targets and benchmark assumptions', ('offence', 'shooting', 'magic'),
        notes='G-phase evidence exists; audit army-level aggregation before calibrating.'),
)


def get_capability_inventory() -> tuple[CapabilityInventoryEntry, ...]:
    """Return immutable inventory records in canonical dashboard order."""
    return _INVENTORY


def get_inventory_entry(metric: str) -> CapabilityInventoryEntry:
    """Look up one inventory record, raising KeyError for unknown metric."""
    for entry in _INVENTORY:
        if entry.metric == metric:
            return entry
    raise KeyError(metric)


def validate_capability_inventory(expected_metrics: tuple[str, ...] = METRIC_NAMES) -> None:
    """Validate structure only; does not assert calibration is complete."""
    names = tuple(entry.metric for entry in _INVENTORY)
    if len(names) != len(set(names)) or names != tuple(expected_metrics):
        raise ValueError('Inventory must match canonical metrics exactly and in order')
    for entry in _INVENTORY:
        if not entry.legacy_provider or not entry.legacy_unit or not entry.mechanical_providers:
            raise ValueError(f'Missing source metadata: {entry.metric}')
        if not entry.mechanical_unit or not entry.evidence_population:
            raise ValueError(f'Missing measurement metadata: {entry.metric}')
        if entry.integration_status not in ('connected', 'diagnostic', 'research'):
            raise ValueError(f'Unknown integration status: {entry.metric}')
        if entry.missing_evidence_policy != 'unavailable_not_zero':
            raise ValueError(f'Invalid missing-evidence policy: {entry.metric}')
        if entry.calibration_status != 'not_agreed':
            raise ValueError(f'Premature calibration claim: {entry.metric}')
        if entry.scenario_mapping_status != 'not_audited':
            raise ValueError(f'Premature scenario-mapping claim: {entry.metric}')
        if entry.metric in entry.dependencies or any(dep not in names for dep in entry.dependencies):
            raise ValueError(f'Invalid metric dependency: {entry.metric}')
