"""DEV-082-A2-3 — consolidated, opt-in mechanical Offence evidence.

Author: Edward Turns (Project Lead)

One ordinary-target, single-engagement diagnostic contract. No production
scoring, calibrated bars, scenario outcomes, or inferred Might expenditure.
Heroic Combat belongs to Command/Control, not Offence.
"""
from dataclasses import dataclass

from combat_benchmark import CombatBenchmark, DEFAULT_COMBAT_BENCHMARK
from command_action_declaration import CommandActionDeclaration
from configured_profile import ConfiguredProfile
from duel_might import DuelMightStrategy
from hero_resource_state import HeroResourceState
from melee_weapon_selection import MeleeWeaponSelection
from offence_charge_state_evidence import (
    ChargeStateOffenceEvidence,
    calculate_charge_state_offence_evidence,
)
from offence_heroic_might_contract import PriorMightSpend
from offence_heroic_probability_evidence import (
    HeroicOffenceProbabilityEvidence,
    calculate_heroic_offence_probability_evidence,
)


@dataclass(frozen=True)
class MechanicalOffenceContract:
    """Conditional probabilities plus explicit evidence/ownership boundaries."""
    baseline: ChargeStateOffenceEvidence
    heroic: HeroicOffenceProbabilityEvidence | None
    unresolved_context: tuple[str, ...]
    evidence_status: str
    target_population: str = 'ordinary_single_wound_benchmark'
    resource_policy: str = 'explicit_actor_reservations_no_inferred_might'
    metric_owner: str = 'offence'
    integration_status: str = 'diagnostic_only_not_connected_to_production'
    dashboard_score: None = None
    scenario_score: None = None

    @property
    def uncharged(self) -> float:
        return self.baseline.uncharged

    @property
    def charged(self) -> float:
        return self.baseline.charged_without_cavalry_bonus

    @property
    def eligible_cavalry_charge(self) -> float:
        return self.baseline.charged_with_cavalry_bonus

    @property
    def weighted_baseline(self) -> float | None:
        return self.baseline.weighted

    @property
    def weighted_enhanced(self) -> float | None:
        return self.heroic.weighted_enhanced if self.heroic is not None else None


def calculate_mechanical_offence_contract(
    attacker: ConfiguredProfile,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    attacker_selection: MeleeWeaponSelection | None = None,
    defender_trapped: bool | None = None,
    target_keywords: tuple[str, ...] | None = None,
    charge_probability: float | None = None,
    cavalry_eligibility_probability: float | None = None,
    actor_id: str | None = None,
    starting_resources: HeroResourceState | None = None,
    prior_spends: tuple[PriorMightSpend, ...] = (),
    heroic_strike: CommandActionDeclaration | None = None,
    duel_might_budget: int = 0,
    duel_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
) -> MechanicalOffenceContract:
    """Unify the existing validated diagnostics without changing their maths.

    No actor/resource pair means baseline-only; it must not request spending.
    An actor/resource pair enables an explicitly budgeted conditional plan.
    None of these cases authorises a new dashboard or army-level metric.
    """
    baseline = calculate_charge_state_offence_evidence(
        attacker, benchmark,
        attacker_selection=attacker_selection,
        defender_trapped=defender_trapped,
        target_keywords=target_keywords,
        charge_probability=charge_probability,
        cavalry_eligibility_probability=cavalry_eligibility_probability,
    )
    if (actor_id is None) != (starting_resources is None):
        raise ValueError('actor_id and starting_resources must be supplied together')
    if actor_id is None and (
        prior_spends or heroic_strike is not None or duel_might_budget != 0
        or duel_might_strategy is not DuelMightStrategy.NEVER
    ):
        raise ValueError('Might allocation requires actor_id and starting_resources')

    heroic = None
    if actor_id is not None:
        heroic = calculate_heroic_offence_probability_evidence(
            actor_id=actor_id,
            attacker=attacker,
            starting_resources=starting_resources,
            prior_spends=prior_spends,
            heroic_strike=heroic_strike,
            duel_might_budget=duel_might_budget,
            duel_might_strategy=duel_might_strategy,
            benchmark=benchmark,
            attacker_selection=attacker_selection,
            defender_trapped=defender_trapped,
            target_keywords=target_keywords,
            charge_probability=charge_probability,
            cavalry_eligibility_probability=cavalry_eligibility_probability,
        )
        # One consolidated interface must not silently change the baseline.
        if (heroic.baseline_uncharged != baseline.uncharged
            or heroic.baseline_charged != baseline.charged_without_cavalry_bonus
            or heroic.baseline_cavalry_eligible != baseline.charged_with_cavalry_bonus
            or heroic.weighted_baseline != baseline.weighted):
            raise ValueError('Heroic diagnostic baseline does not match charge-state evidence')

    unresolved = []
    if attacker_selection is None:
        unresolved.append('weapon_choice_implicit')
    if defender_trapped is None:
        unresolved.append('trap_state_unknown_untrapped_reference')
    if target_keywords is None:
        unresolved.append('target_keywords_unspecified')
    if charge_probability is None:
        unresolved.append('charge_probability_unknown')
    if cavalry_eligibility_probability is None:
        unresolved.append('cavalry_eligibility_probability_unknown')
    if heroic is not None and heroic.evidence_status == 'unsupported_duel_context_not_evaluated':
        unresolved.append('enhanced_duel_context_unsupported')

    status = (
        'conditional_enhancement_unsupported'
        if 'enhanced_duel_context_unsupported' in unresolved else
        'conditional_evidence_not_calibrated'
        if heroic is not None and (
            heroic.allocation.heroic_strike_reserved or heroic.allocation.duel_might_reserved
        ) else
        'baseline_only_not_calibrated'
    )
    return MechanicalOffenceContract(
        baseline=baseline, heroic=heroic,
        unresolved_context=tuple(unresolved), evidence_status=status,
    )
