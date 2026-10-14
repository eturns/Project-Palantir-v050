"""DEV-077S-I2-I-A4: declarative cross-capability dependency and overlap audit.

No scoring, inferred battlefield outcomes, or automatic adjustment. The records
pin known sharing hazards for review during I2-I-B calibration.
"""
from dataclasses import dataclass

from unified_capability_inventory import METRIC_NAMES

SOURCE_COMMIT = '51ad0f1'


@dataclass(frozen=True)
class SharedEvidenceRisk:
    identifier: str
    capabilities: tuple[str, ...]
    shared_evidence: str
    risk: str
    required_control: str
    disposition: str = 'needs_calibration_contract'


RISKS = (
    SharedEvidenceRisk('magic_control', ('magic', 'control'),
        'Will spending, spell repertoire and Control spell effects',
        'Counting the same cast as independent Magic production and Control output',
        'Separate casting capacity from realised control; reconcile Will once'),
    SharedEvidenceRisk('offence_hero_hunting', ('offence', 'hero_hunting'),
        'Melee attack events, Might and wounds inflicted',
        'Counting the same damage event twice as general offence and hero elimination',
        'Use distinct target populations and a shared feasible event/resource allocation'),
    SharedEvidenceRisk('shooting_hero_hunting', ('shooting', 'hero_hunting'),
        'Ranged attacks, firing opportunities and target damage',
        'Duplicating ranged damage as hero-hunting output',
        'Keep general shooting benchmark separate from target-specific conditional plans'),
    SharedEvidenceRisk('mobility_objective', ('mobility', 'objective'),
        'Movement, terrain constraints and objective reachability',
        'Adding mobility value twice when reachability is an objective input',
        'Separate mobility potential from scenario-conditioned control/presence'),
    SharedEvidenceRisk('defence_objective', ('defence', 'objective'),
        'Model survival and objective endurance',
        'Counting the same survivability projection as independent objective endurance',
        'Use survival as a conditional objective input, not an extra standalone bonus'),
    SharedEvidenceRisk('courage_control', ('courage', 'control'),
        'Terror, Harbinger of Evil and affected target behaviour',
        'Reusing one failed Courage test as two independent outcomes',
        'Account for the test in Courage; count verified applied control effects only'),
    SharedEvidenceRisk('command_offence_mobility', ('command', 'offence', 'mobility'),
        'Heroic Actions, recipients and shared Might',
        'Treating command authority and the attacks/movement enabled as independent resources',
        'Use one Might ledger and report authorised actions separately from resulting effects'),
    SharedEvidenceRisk('command_hero_hunting', ('command', 'hero_hunting'),
        'Heroic Strike and other Might-funded attack plans',
        'Double spending Might on Command and hero elimination plans',
        'Reconcile the same per-model Might pool before evaluating either claim'),
    SharedEvidenceRisk('control_hero_hunting', ('control', 'hero_hunting'),
        'Will-funded magical methods against hero targets',
        'Double spending Will or treating control effects as verified elimination',
        'Require shared Will accounting and target-specific executable evidence'),
)


@dataclass(frozen=True)
class OverlapAudit:
    source_commit: str
    risk_count: int
    capabilities_covered: tuple[str, ...]
    scoring_changed: bool = False


def get_overlap_risks(metric: str | None = None) -> tuple[SharedEvidenceRisk, ...]:
    if metric is not None and metric not in METRIC_NAMES:
        raise KeyError(metric)
    return tuple(r for r in RISKS if metric is None or metric in r.capabilities)


def validate_overlap_audit() -> OverlapAudit:
    ids = tuple(r.identifier for r in RISKS)
    if len(ids) != len(set(ids)):
        raise ValueError('Overlap identifiers must be unique')
    for risk in RISKS:
        if len(risk.capabilities) < 2 or len(set(risk.capabilities)) != len(risk.capabilities):
            raise ValueError('Overlap must refer to distinct capabilities')
        if any(m not in METRIC_NAMES for m in risk.capabilities):
            raise ValueError('Unknown capability in overlap')
        if not all((risk.shared_evidence, risk.risk, risk.required_control)):
            raise ValueError('Missing evidence, risk or required control')
        if risk.disposition != 'needs_calibration_contract':
            raise ValueError('Unapproved calibration disposition')
    return OverlapAudit(SOURCE_COMMIT, len(RISKS),
        tuple(m for m in METRIC_NAMES if any(m in r.capabilities for r in RISKS)))
