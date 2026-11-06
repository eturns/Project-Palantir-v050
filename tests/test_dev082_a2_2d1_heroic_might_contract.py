"""DEV-082-A2-2D-1 — diagnostic-only Heroic Strike and Duel Might contracts.
Author: Edward Turns (Project Lead)
"""
import pytest

from command_action_declaration import CommandActionDeclaration, CommandCheck
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from duel_might import DuelMightStrategy
from hero_resource_state import HeroResourceState
from heroic_action import HeroicAction
from offence_heroic_might_contract import PriorMightSpend, plan_offence_heroic_might
from profiles import Profile


def fighter(*, actions=('HEROIC_STRIKE',)):
    p = Profile(
        id='DEV082_HERO', name='Diagnostic hero', points=100,
        movement=6, fight=5, shooting='4+', strength=4, defence=6,
        attacks=2, wounds=2, courage='4+', intelligence='4+',
        might=3, will=1, fate=1, max_in_army=1,
    )
    p.heroic_actions = [HeroicAction(id=a, name=a, category=RuleCategory.OFFENCE) for a in actions]
    return ConfiguredProfile(profile=p)


def strike(*, actor='HERO#1', event='strike-1', timing=CommandCheck.VERIFIED_TRUE,
           activation=CommandCheck.VERIFIED_TRUE, battlefield=CommandCheck.VERIFIED_TRUE,
           action='HEROIC_STRIKE', cost=1):
    return CommandActionDeclaration(
        event_id=event, actor_id=actor, heroic_action_id=action, turn=1,
        timing_legal=timing, activation_legal=activation,
        battlefield_legal=battlefield, might_cost=cost,
    )


def plan(**kw):
    return plan_offence_heroic_might(
        actor_id='HERO#1', attacker=fighter(),
        starting_resources=HeroResourceState(remaining_might=3, remaining_will=1, remaining_fate=1),
        **kw,
    )


def test_baseline_without_spending_keeps_all_might_and_no_score():
    e = plan()
    assert (e.remaining_might, e.heroic_strike_reserved, e.duel_might_reserved) == (3, 0, 0)
    assert e.enhanced_offence_probability is None and e.dashboard_score is None and e.scenario_score is None


def test_verified_strike_reserves_one_might_only():
    e = plan(heroic_strike=strike())
    assert e.heroic_strike_reserved == 1 and e.remaining_might == 2
    assert e.action_status == 'permitted_might_reserved_effect_not_evaluated'


def test_strike_and_duel_budget_reserve_exclusively():
    e = plan(heroic_strike=strike(), duel_might_budget=1,
             duel_might_strategy=DuelMightStrategy.MINIMUM_TO_WIN)
    assert (e.heroic_strike_reserved, e.duel_might_reserved, e.remaining_might) == (1, 1, 1)


def test_prior_hero_hunting_spend_leaves_no_budget_for_two_more():
    with pytest.raises(ValueError, match='Cannot spend more Might'):
        plan(prior_spends=(PriorMightSpend('hero-hunt-1', 'hero_hunting', 2),),
             heroic_strike=strike(), duel_might_budget=1,
             duel_might_strategy=DuelMightStrategy.MINIMUM_TO_WIN)


def test_valid_prior_spend_is_accounted_once():
    e = plan(prior_spends=(PriorMightSpend('command-1', 'command', 1),),
             heroic_strike=strike(), duel_might_budget=1,
             duel_might_strategy=DuelMightStrategy.MINIMUM_TO_WIN)
    assert (e.prior_might_spent, e.remaining_might) == (1, 0)


def test_unknown_strike_opportunity_fails_closed():
    with pytest.raises(ValueError, match='unverified_opportunity'):
        plan(heroic_strike=strike(timing=CommandCheck.UNKNOWN))


def test_strike_not_on_profile_is_rejected():
    with pytest.raises(ValueError, match='not on this model profile'):
        plan_offence_heroic_might(actor_id='HERO#1', attacker=fighter(actions=()),
                                 starting_resources=HeroResourceState(remaining_might=3),
                                 heroic_strike=strike())


def test_heroic_combat_is_not_offence_contract():
    with pytest.raises(ValueError, match='Only Heroic Strike'):
        plan(heroic_strike=strike(action='HEROIC_COMBAT'))


def test_duplicate_prior_events_rejected():
    with pytest.raises(ValueError, match='duplicated'):
        plan(prior_spends=(PriorMightSpend('e1', 'command', 1),
                           PriorMightSpend('e1', 'hero_hunting', 1)))


def test_strike_event_cannot_duplicate_prior_spend():
    with pytest.raises(ValueError, match='duplicates prior'):
        plan(prior_spends=(PriorMightSpend('strike-1', 'command', 1),),
             heroic_strike=strike())


def test_wrong_actor_rejected():
    with pytest.raises(ValueError, match='resource owner'):
        plan(heroic_strike=strike(actor='HERO#2'))


def test_strategy_requires_explicit_positive_budget():
    with pytest.raises(ValueError, match='together'):
        plan(duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)


def test_budget_requires_strategy():
    with pytest.raises(ValueError, match='together'):
        plan(duel_might_budget=1)


def test_invalid_heroic_strike_cost_is_rejected():
    with pytest.raises(ValueError, match='one-Might'):
        plan(heroic_strike=strike(cost=0))


def test_resources_not_mutated_by_plan():
    starting = HeroResourceState(remaining_might=3, remaining_will=1, remaining_fate=1)
    e = plan_offence_heroic_might(actor_id='HERO#1', attacker=fighter(), starting_resources=starting,
                                 heroic_strike=strike())
    assert starting.remaining_might == 3
    assert e.remaining_might == 2
