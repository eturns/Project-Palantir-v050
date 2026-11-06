"""DEV-082-A2-2D-1: conditional Offence Heroic Strike / Duel Might contract.

Author: Edward Turns (Project Lead)

Diagnostic-only. No new combat scoring, dashboard values, scenario effects or
inferred Might expenditure. Command authorises Heroic Strike; Duel Might is a
separately reserved budget. The result is an allocation *plan*, not execution.
Heroic Combat is deliberately outside the Offence contract.
"""
from dataclasses import dataclass

from command_action_declaration import (
    CommandActionDeclaration, CommandCheck, CommandDecision,
    evaluate_command_declaration,
)
from configured_profile import ConfiguredProfile
from duel_might import DuelMightStrategy
from hero_resource_state import HeroResourceState
from hero_resource_spending import spend_might

HEROIC_STRIKE_ID = 'HEROIC_STRIKE'


@dataclass(frozen=True)
class PriorMightSpend:
    event_id: str
    domain: str
    amount: int

    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError('prior event_id must be nonblank')
        if not isinstance(self.domain, str) or not self.domain.strip():
            raise ValueError('prior domain must be nonblank')
        if type(self.amount) is not int or self.amount < 0:
            raise ValueError('prior Might amount must be a nonnegative integer')


@dataclass(frozen=True)
class OffenceHeroicMightEvidence:
    actor_id: str
    starting_might: int
    prior_might_spent: int
    heroic_strike_reserved: int
    duel_might_reserved: int
    duel_might_strategy: str
    remaining_might: int
    declared_heroic_strike: bool
    action_status: str
    evidence_status: str = 'verified_allocations_only_effect_not_evaluated'
    enhanced_offence_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def plan_offence_heroic_might(
    *,
    actor_id: str,
    attacker: ConfiguredProfile,
    starting_resources: HeroResourceState,
    prior_spends: tuple[PriorMightSpend, ...] = (),
    heroic_strike: CommandActionDeclaration | None = None,
    duel_might_budget: int = 0,
    duel_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
) -> OffenceHeroicMightEvidence:
    """Build one actor's exclusive Might allocation, without rating effects.

    The caller supplies actual fielded-actor ID and up-to-date resource state.
    Prior spends must be reconciled for that same actor from other domains.
    All Heroic Strike opportunity checks must be VERIFIED_TRUE; unresolved
    declarations fail closed rather than being treated as successful.
    The Duel budget is conservatively *reserved in full*, not predicted spent.
    """
    if not isinstance(actor_id, str) or not actor_id.strip():
        raise ValueError('actor_id must be nonblank')
    if not isinstance(attacker, ConfiguredProfile):
        raise TypeError('attacker must be ConfiguredProfile')
    if not isinstance(starting_resources, HeroResourceState):
        raise TypeError('starting_resources must be HeroResourceState')
    if not isinstance(prior_spends, tuple) or any(not isinstance(s, PriorMightSpend) for s in prior_spends):
        raise TypeError('prior_spends must contain PriorMightSpend')
    if type(duel_might_budget) is not int or duel_might_budget < 0:
        raise ValueError('duel_might_budget must be nonnegative integer')
    if not isinstance(duel_might_strategy, DuelMightStrategy):
        raise TypeError('duel_might_strategy must be DuelMightStrategy')
    if (duel_might_budget == 0) != (duel_might_strategy is DuelMightStrategy.NEVER):
        raise ValueError('Duel Might allocation and strategy must be supplied together')

    event_ids = [s.event_id for s in prior_spends]
    if len(set(event_ids)) != len(event_ids):
        raise ValueError('prior Might event_id cannot be duplicated')
    current = starting_resources
    for spend in prior_spends:
        current = spend_might(current, spend.amount)

    strike_reserved = 0
    action_status = 'not_declared'
    if heroic_strike is not None:
        if not isinstance(heroic_strike, CommandActionDeclaration):
            raise TypeError('heroic_strike must be CommandActionDeclaration')
        if heroic_strike.event_id in event_ids:
            raise ValueError('Heroic Strike event duplicates prior spend')
        if heroic_strike.actor_id != actor_id:
            raise ValueError('Heroic Strike actor does not match the resource owner')
        if heroic_strike.heroic_action_id != HEROIC_STRIKE_ID:
            raise ValueError('Only Heroic Strike is permitted by Offence contract')
        available = tuple(a.id for a in attacker.profile.heroic_actions)
        if HEROIC_STRIKE_ID not in available:
            raise ValueError('Heroic Strike is not on this model profile')
        # Reuse the existing Command authorisation and consumption contract.
        decision = evaluate_command_declaration(
            heroic_strike,
            known_action_ids=(HEROIC_STRIKE_ID,),
            available_action_ids=(HEROIC_STRIKE_ID,),
            resources=current,
        )
        if decision.decision is not CommandDecision.PERMITTED:
            raise ValueError('Heroic Strike not permitted: ' + decision.reason)
        if heroic_strike.might_cost != 1:
            raise ValueError('Heroic Strike requires a verified one-Might declaration')
        current = decision.remaining_resources
        strike_reserved = decision.might_spent
        action_status = 'permitted_might_reserved_effect_not_evaluated'

    current = spend_might(current, duel_might_budget)
    return OffenceHeroicMightEvidence(
        actor_id=actor_id,
        starting_might=starting_resources.remaining_might,
        prior_might_spent=sum(s.amount for s in prior_spends),
        heroic_strike_reserved=strike_reserved,
        duel_might_reserved=duel_might_budget,
        duel_might_strategy=duel_might_strategy.value,
        remaining_might=current.remaining_might,
        declared_heroic_strike=heroic_strike is not None,
        action_status=action_status,
    )
