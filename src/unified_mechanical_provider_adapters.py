"""DEV-077S-I2-I-C2: read-only provider evidence adapters.

No provider is executed and no production or scenario score is generated.
This module upgrades C1's unavailable placeholders only when a verified,
explicit provider contract is supplied. Conditional sub-measures remain PARTIAL.
"""
from dataclasses import dataclass, replace
from math import isfinite
from typing import Mapping

from unified_calibration_contract import EvidenceAvailability, RawMeasurement
from unified_capability_inventory import METRIC_NAMES
from unified_real_army_measurements import MechanicalArmySnapshot

PROVIDER_METRICS = ('mobility', 'magic', 'courage', 'control', 'command', 'objective', 'hero_hunting')


@dataclass(frozen=True)
class ProviderEvidenceBundle:
    mobility: object | None = None
    magic: object | None = None
    courage: object | None = None
    control: object | None = None
    command: object | None = None
    objective: object | None = None
    hero_hunting: object | None = None


def _number(value):
    return type(value) in (int, float) and isfinite(value)


def _measure(metric, value, unit, population, provenance, *, partial=False, issue=None, assumptions=()):
    if issue is not None or not _number(value):
        return RawMeasurement(metric, None, unit, population, provenance,
                              EvidenceAvailability.UNAVAILABLE,
                              assumptions=tuple(assumptions),
                              unresolved=(issue or 'numerical_evidence_not_verified',))
    return RawMeasurement(metric, float(value), unit, population, provenance,
                          EvidenceAvailability.PARTIAL if partial else EvidenceAvailability.AVAILABLE,
                          assumptions=tuple(assumptions),
                          unresolved=('conditional_submeasure_not_full_capability',) if partial else ())


def _property(obj, name):
    return getattr(obj, name, None) if obj is not None else None


def _submeasure(obj, field, metric_id, unit):
    m = _property(obj, field)
    if m is None or _property(m, 'metric_id') != metric_id or _property(m, 'unit') != unit:
        return None
    return m if _number(_property(m, 'value')) else None


def extract_provider_measurement(metric: str, provider: object | None) -> RawMeasurement:
    """Return a carefully scoped raw axis or an unavailable measurement.

    The three available axes below are NOT complete multidimensional capability
    scores; no summation or blending of independent mechanical axes occurs.
    """
    if metric not in PROVIDER_METRICS:
        raise KeyError(metric)
    provenance = f'C2 provider: {metric}'
    if metric == 'mobility':
        m = _submeasure(provider, 'open_ground', 'mobility.open_ground.mean',
                        'movement_accessibility_index')
        return _measure(metric, _property(m, 'value'), 'movement_accessibility_index',
                        'fielded models; open terrain; base-size adjustment',
                        'mobility_integration_contract.open_ground',
                        issue=None if m is not None else 'mobility_open_ground_measure_missing_or_mismatched',
                        assumptions=_property(m, 'assumptions') or ())
    if metric == 'courage':
        m = _submeasure(provider, 'friendly_reliability', 'courage.friendly.pass_probability', 'probability')
        return _measure(metric, _property(m, 'value'), 'probability',
                        'quantity-weighted hypothetical standard Courage test',
                        'courage_integration_contract.friendly_reliability',
                        issue=None if m is not None else 'courage_friendly_probability_missing_or_mismatched',
                        assumptions=_property(m, 'assumptions') or ())
    if metric == 'magic':
        chance = _property(provider, 'one_will_probability_weighted_mean')
        casters = _property(provider, 'caster_count')
        if type(casters) is not int or casters <= 0 or not _number(chance) or not 0 <= chance <= 1:
            return _measure(metric, None, 'probability_per_declared_single_attempt',
                            'spellcaster-only, one-Will attempt conditional',
                            'mechanical_magic_army_contract.one_will_probability_weighted_mean',
                            issue='magic_one_will_attempt_probability_unavailable')
        return _measure(metric, chance, 'probability_per_declared_single_attempt',
                        'spellcaster-only, one-Will attempt conditional',
                        'mechanical_magic_army_contract.one_will_probability_weighted_mean',
                        partial=True,
                        assumptions=_property(provider, 'assumptions') or ())
    # Roster / declared-event / scenario conditional evidence does not establish
    # a scalar measure that can be honestly sampled across armies.
    reasons = {
        'control': 'declared_control_events_do_not_establish_army_control_output',
        'command': 'heroic_action_authority_and_coverage_are_not_one_scalar',
        'objective': 'verified_scenario_rules_and_position_required_no_generic_scalar',
        'hero_hunting': 'target_specific_conditional_plan_no_joint_army_probability',
    }
    return _measure(metric, None, 'no_approved_scalar_unit',
                    'requires explicit battle or scenario context', provenance,
                    issue=reasons[metric])


def extend_mechanical_army_snapshot(snapshot: MechanicalArmySnapshot,
                                    providers: ProviderEvidenceBundle) -> MechanicalArmySnapshot:
    """Replace only C1 placeholders, preserving existing raw outputs exactly."""
    if not isinstance(snapshot, MechanicalArmySnapshot):
        raise TypeError('snapshot must be MechanicalArmySnapshot')
    if not isinstance(providers, ProviderEvidenceBundle):
        raise TypeError('providers must be ProviderEvidenceBundle')
    by_metric = {m.metric: m for m in snapshot.measurements}
    if len(by_metric) != len(METRIC_NAMES) or tuple(by_metric) != METRIC_NAMES:
        raise ValueError('snapshot must contain ten canonical measurements')
    output = []
    for name in METRIC_NAMES:
        previous = by_metric[name]
        if name not in PROVIDER_METRICS or previous.availability is not EvidenceAvailability.UNAVAILABLE:
            output.append(previous)
        else:
            output.append(extract_provider_measurement(name, getattr(providers, name)))
    return replace(snapshot, measurements=tuple(output),
                   available_count=sum(m.availability is EvidenceAvailability.AVAILABLE for m in output),
                   unresolved_metrics=tuple(m.metric for m in output if m.availability is not EvidenceAvailability.AVAILABLE),
                   production_scoring_enabled=False)
