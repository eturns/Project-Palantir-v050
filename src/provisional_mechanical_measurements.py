"""DEV-077S-I2-I-P2-C2: read-only, benchmark-matched mechanical dashboard evidence.

This module deliberately contains no scenario, optimiser, or rating calculation.
A failed or unavailable mechanical context is not equivalent to an observed zero.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

from provisional_calibration import CONDITIONAL, EVALUATED, NOT_EVALUATED

METRICS = (
    'offence_density', 'stationary_shooting',
    'open_ground_mobility', 'courage_reliability',
)


@dataclass(frozen=True)
class ProvisionalMechanicalEvidence:
    values: dict[str, float] = field(default_factory=dict)
    statuses: dict[str, str] = field(default_factory=dict)
    reasons: dict[str, str] = field(default_factory=dict)


def _measurement(evidence, key, operation):
    """Keep an unavailable metric unscored, without hiding its cause."""
    try:
        value = float(operation())
        if not math.isfinite(value) or value < 0:
            raise ValueError('nonfinite or negative mechanical measurement')
    except (ValueError, TypeError, AttributeError, KeyError, LookupError) as error:
        evidence.statuses[key] = CONDITIONAL
        evidence.reasons[key] = f'{type(error).__name__}: {error}'
    else:
        evidence.values[key] = value
        evidence.statuses[key] = EVALUATED


def collect_provisional_mechanical_evidence(army) -> ProvisionalMechanicalEvidence:
    """Reproduce the D1/D2 baseline contexts, not legacy capability scores.

    D1 benchmark target is a hypothetical F4 S4 D6 A1 configured profile.
    Shooting is stationary versus that target, in range and unobstructed.
    Mobility is the base-size-adjusted open-ground accessibility index.
    Courage is own-test reliability with no Stand Fast/positional support.
    """
    evidence = ProvisionalMechanicalEvidence(
        statuses={key: NOT_EVALUATED for key in METRICS}
    )
    if army is None:
        return evidence
    from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
    from army_offence_capability import calculate_army_offensive_output_density
    from mobility_integration_contract import build_mobility_integration_contract
    from army_shooting_capability import calculate_army_shooting_output_density
    from courage_integration_contract import build_courage_integration_contract
    from configured_profile import ConfiguredProfile
    from profiles import Profile

    # Reproduce the frozen D1 audit's benchmark_target() exactly without
    # importing a repository-root audit script from the packaged desktop app.
    b = DEFAULT_COMBAT_BENCHMARK
    target = ConfiguredProfile(profile=Profile(
        id='D1_BENCHMARK', name='D1 Benchmark', points=0,
        movement=6, fight=b.fight, shooting='4+', strength=b.strength,
        defence=b.defence, attacks=b.attacks, wounds=b.wounds,
        courage='4+', intelligence='4+', might=0, will=0, fate=0,
        max_in_army=0,
    ))
    _measurement(evidence, 'offence_density',
                 lambda: calculate_army_offensive_output_density(
                     army, DEFAULT_COMBAT_BENCHMARK))
    _measurement(evidence, 'stationary_shooting',
                 lambda: calculate_army_shooting_output_density(
                     army=army, defender=target))
    _measurement(evidence, 'open_ground_mobility',
                 lambda: build_mobility_integration_contract(army).open_ground.value)
    _measurement(evidence, 'courage_reliability',
                 lambda: build_courage_integration_contract(
                     army, target).friendly_reliability.value)
    return evidence
