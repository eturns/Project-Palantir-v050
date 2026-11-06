"""DEV-082-A2-2D-2 — conditional Heroic Strike / Duel Might Offence evidence.

Author: Edward Turns (Project Lead)

Diagnostic-only. Reuses DEV-082 charge-state elimination results, Command's
Might authorisation contract, and the canonical basic Duel probability engine.
No public score, scenarios, optimiser, or calibration are modified.
The entire Duel Might budget is RESERVED, not a prediction of actual spending.
Heroic Combat is intentionally excluded from Offence.
"""
from dataclasses import dataclass
from math import isclose

from combat_benchmark import CombatBenchmark, DEFAULT_COMBAT_BENCHMARK
from combat_context import CombatContext, EngagementRole
from configured_duel_probability import calculate_configured_duel_probability
from configured_profile import ConfiguredProfile
from duel_might import DuelMightStrategy
from duel_probability import calculate_basic_duel_probability
from effective_attacks import get_effective_attacks
from hero_resource_state import HeroResourceState
from hunt_master import get_hunt_master_fight_bonus
from mechanical_effect_target import MechanicalEffectTarget
from melee_weapon_selection import MeleeWeaponSelection
from offence_charge_state_evidence import (
    _benchmark_defender, _state_score, calculate_charge_state_offence_evidence,
)
from offence_heroic_might_contract import (
    OffenceHeroicMightEvidence, PriorMightSpend, plan_offence_heroic_might,
)
from roll_modifier_effect_resolver import resolved_duel_modifier
from wargear_mechanical_effect_definitions import get_wargear_mechanical_effect_definitions
from command_action_declaration import CommandActionDeclaration


@dataclass(frozen=True)
class HeroicOffenceProbabilityEvidence:
    allocation: OffenceHeroicMightEvidence
    baseline_uncharged: float
    baseline_charged: float
    baseline_cavalry_eligible: float
    enhanced_uncharged: float | None
    enhanced_charged: float | None
    enhanced_cavalry_eligible: float | None
    weighted_baseline: float | None
    weighted_enhanced: float | None
    evidence_status: str
    dashboard_score: None = None
    scenario_score: None = None


def _enhanced_state(attacker, defender, *, charged, cavalry_eligible,
                    attacker_selection, defender_trapped, allocation):
    context = CombatContext(
        engagement_role=EngagementRole.CHARGED if charged else EngagementRole.WAS_CHARGED,
        charged_only_infantry=cavalry_eligible,
        resolving_exclusively_against_infantry=cavalry_eligible,
    )
    enemy_context = CombatContext(engagement_role=EngagementRole.WAS_CHARGED)
    configured_duel = calculate_configured_duel_probability(
        attacker, defender, attacker_selection=attacker_selection,
        attacker_context=context, defender_context=enemy_context,
    )
    a_defs = tuple(d for d in get_wargear_mechanical_effect_definitions(
        attacker, selection=attacker_selection,
    ) if d.effect.target is MechanicalEffectTarget.DUEL_ROLL)
    d_defs = tuple(d for d in get_wargear_mechanical_effect_definitions(
        defender,
    ) if d.effect.target is MechanicalEffectTarget.DUEL_ROLL)
    kwargs = dict(
        attacker_attacks=get_effective_attacks(attacker, context, selection=attacker_selection),
        attacker_fight=attacker.effective_fight + get_hunt_master_fight_bonus(attacker, context),
        defender_attacks=get_effective_attacks(defender, enemy_context),
        defender_fight=defender.effective_fight + get_hunt_master_fight_bonus(defender, enemy_context),
        attacker_modifier=resolved_duel_modifier(a_defs),
        defender_modifier=resolved_duel_modifier(d_defs),
    )
    ordinary_duel = calculate_basic_duel_probability(**kwargs)
    # No credit if the simplified Duel path fails to reproduce the configured
    # baseline; this guards conditional rules not represented by its arguments.
    if not isclose(ordinary_duel.attacker_win_probability,
                   configured_duel.attacker_win_probability, abs_tol=1e-12):
        return None
    enhanced_duel = calculate_basic_duel_probability(
        **kwargs,
        attacker_heroic_strike_active=bool(allocation.heroic_strike_reserved),
        attacker_might_available=allocation.duel_might_reserved,
        attacker_might_strategy=DuelMightStrategy(allocation.duel_might_strategy),
    )
    baseline = _state_score(
        attacker, defender, charged=charged, cavalry_eligible=cavalry_eligible,
        attacker_selection=attacker_selection, defender_trapped=defender_trapped,
    )
    # Same conditional damage distribution; only the Duel result differs.
    if configured_duel.attacker_win_probability <= 0:
        return None
    result = baseline * enhanced_duel.attacker_win_probability / configured_duel.attacker_win_probability
    return min(1.0, max(0.0, result))


def calculate_heroic_offence_probability_evidence(
    *,
    actor_id: str,
    attacker: ConfiguredProfile,
    starting_resources: HeroResourceState,
    prior_spends: tuple[PriorMightSpend, ...] = (),
    heroic_strike: CommandActionDeclaration | None = None,
    duel_might_budget: int = 0,
    duel_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    attacker_selection: MeleeWeaponSelection | None = None,
    defender_trapped: bool | None = None,
    target_keywords: tuple[str, ...] | None = None,
    charge_probability: float | None = None,
    cavalry_eligibility_probability: float | None = None,
) -> HeroicOffenceProbabilityEvidence:
    """Expose ordinary and authorised-Might combat probabilities separately.

    All combat contexts match the A2-2C charge evidence. Unknown charge
    likelihood remains unweighted; no Might or Heroic Strike is inferred.
    The benchmark has no defender Might, Fate, weapon or special rules.
    """
    allocation = plan_offence_heroic_might(
        actor_id=actor_id, attacker=attacker,
        starting_resources=starting_resources, prior_spends=prior_spends,
        heroic_strike=heroic_strike, duel_might_budget=duel_might_budget,
        duel_might_strategy=duel_might_strategy,
    )
    baseline = calculate_charge_state_offence_evidence(
        attacker, benchmark, attacker_selection=attacker_selection,
        defender_trapped=defender_trapped, target_keywords=target_keywords,
        charge_probability=charge_probability,
        cavalry_eligibility_probability=cavalry_eligibility_probability,
    )
    b = (baseline.uncharged, baseline.charged_without_cavalry_bonus,
         baseline.charged_with_cavalry_bonus)
    if not (allocation.heroic_strike_reserved or allocation.duel_might_reserved):
        # No promised enhancement: preserving exact baseline values is safer
        # than running a second, potentially narrower, Duel resolver.
        e = b
        status = 'no_might_allocated_baseline_only'
    else:
        defender = _benchmark_defender(benchmark, baseline.target_keywords)
        e = tuple(_enhanced_state(
            attacker, defender, charged=charged, cavalry_eligible=eligible,
            attacker_selection=attacker_selection,
            defender_trapped=defender_trapped is True, allocation=allocation,
        ) for charged, eligible in ((False, False), (True, False), (True, True)))
        status = ('verified_conditional_probability_not_calibrated'
                  if all(x is not None for x in e)
                  else 'unsupported_duel_context_not_evaluated')
    weighted = None
    if (baseline.weighted is not None and all(x is not None for x in e)):
        p, q = charge_probability, cavalry_eligibility_probability
        weighted = (1-p)*e[0] + p*((1-q)*e[1] + q*e[2])
    return HeroicOffenceProbabilityEvidence(
        allocation, *b, *e, baseline.weighted, weighted, status,
    )
