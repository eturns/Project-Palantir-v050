"""DEV-082-A3-2A — opt-in, read-only shadow Offence comparison.

Author: Edward Turns (Project Lead)

This module is never imported by the production display path. It deliberately
DOES NOT compute a replacement army Offence density from A2 conditional states:
charge/trap/weapon opportunities are unverified without battlefield evidence.
No scores, calibration, scenario results or Army objects are modified.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from combat_benchmark import CombatBenchmark, DEFAULT_COMBAT_BENCHMARK
from army_offence_capability import calculate_army_offensive_output_density
from offence_mechanical_contract import calculate_mechanical_offence_contract


@dataclass(frozen=True)
class ShadowProfileEvidence:
    profile_id: str
    quantity: int
    uncharged_probability: float
    charged_probability: float
    cavalry_eligible_probability: float
    weighted_probability: float | None
    unresolved_context: tuple[str, ...]
    evidence_status: str


@dataclass(frozen=True)
class ShadowOffenceEvidence:
    enabled: bool
    legacy_raw_density: float | None
    profiles: tuple[ShadowProfileEvidence, ...]
    candidate_raw_density: None = None
    comparable: bool = False
    evidence_status: str = 'not_requested'
    reason: str = 'explicit_opt_in_required'
    metric_id: str = 'offence_density'
    source: str = 'DEV-082-A3-2A'
    integration_status: str = 'diagnostic_only_no_production_wiring'
    dashboard_score: None = None
    scenario_score: None = None


def collect_shadow_offence_evidence(
    army,
    *,
    enabled: bool = False,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
) -> ShadowOffenceEvidence:
    """Read the legacy density and A2 model evidence only when opted in.

    No probabilities for charge, cavalry eligibility, trapping, target keyword
    or Might expenditure are supplied. Therefore all model evidence is
    conditional, and no army-level A2 density or calibration rating is emitted.

    Exceptions from unsupported combat mechanics intentionally propagate to
    the diagnostic caller. They must never be silently converted to zero.
    """
    if type(enabled) is not bool:
        raise TypeError('enabled must be bool')
    if not enabled:
        return ShadowOffenceEvidence(enabled=False, legacy_raw_density=None, profiles=())
    if army is None or not callable(getattr(army, 'total_points', None)) or not hasattr(army, 'entries'):
        raise TypeError('enabled shadow requires an Army-like object')
    points = army.total_points()
    if type(points) not in (int, float) or not math.isfinite(points) or points < 0:
        raise ValueError('army points must be finite and nonnegative')
    legacy = float(calculate_army_offensive_output_density(army, benchmark))
    if not math.isfinite(legacy) or legacy < 0:
        raise ValueError('legacy Offence density must be finite and nonnegative')

    profiles = []
    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        qty = entry.quantity
        if type(qty) is not int or qty < 1:
            raise ValueError('fielded quantity must be a positive integer')
        configured = entry.configured_profile
        contract = calculate_mechanical_offence_contract(configured, benchmark)
        if contract.heroic is not None or contract.weighted_baseline is not None:
            raise ValueError('unqualified shadow must not infer Might or weighted encounters')
        probabilities = (contract.uncharged, contract.charged, contract.eligible_cavalry_charge)
        if any(type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities):
            raise ValueError('diagnostic probabilities must be finite and between zero and one')
        profiles.append(ShadowProfileEvidence(
            profile_id=configured.profile.id,
            quantity=qty,
            uncharged_probability=contract.uncharged,
            charged_probability=contract.charged,
            cavalry_eligible_probability=contract.eligible_cavalry_charge,
            weighted_probability=None,
            unresolved_context=contract.unresolved_context,
            evidence_status=contract.evidence_status,
        ))
    return ShadowOffenceEvidence(
        enabled=True,
        legacy_raw_density=legacy,
        profiles=tuple(profiles),
        evidence_status='conditional_not_comparable',
        reason='no_verified_army_level_charge_trap_weapon_or_might_allocation',
    )
