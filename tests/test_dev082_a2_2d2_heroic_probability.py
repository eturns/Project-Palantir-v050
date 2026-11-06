"""DEV-082-A2-2D-2 conditional Heroic Strike/Might diagnostic tests.
Author: Edward Turns (Project Lead)
"""
import pytest

from command_action_declaration import CommandActionDeclaration, CommandCheck
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from duel_might import DuelMightStrategy
from hero_resource_state import HeroResourceState
from heroic_action import HeroicAction
from melee_weapon_selection import MeleeWeaponSelection
from offence_heroic_probability_evidence import calculate_heroic_offence_probability_evidence
from profiles import Profile
from wargear import Wargear


def fighter(*, two_handed=False, strike=True):
    p = Profile(
        id='DEV082_D2_HERO', name='Offence probability hero', points=80,
        movement=6, fight=3, shooting='4+', strength=4, defence=5,
        attacks=2, wounds=2, courage='4+', intelligence='4+',
        might=3, will=0, fate=0, max_in_army=1,
    )
    if strike:
        p.heroic_actions.append(HeroicAction(
            id='HEROIC_STRIKE', name='Heroic Strike', category=RuleCategory.OFFENCE))
    if two_handed:
        p.default_wargear.append(Wargear(id='WG_TWO_HANDED_WEAPON', name='Two-handed Weapon'))
    return ConfiguredProfile(p)


def declaration(*, check=CommandCheck.VERIFIED_TRUE, action='HEROIC_STRIKE'):
    return CommandActionDeclaration(
        event_id='dev082-strike-1', actor_id='DEV082_D2_HERO#1',
        heroic_action_id=action, turn=1,
        timing_legal=check, activation_legal=check,
        battlefield_legal=check, might_cost=1,
    )


def evidence(attacker=None, **kwargs):
    return calculate_heroic_offence_probability_evidence(
        actor_id='DEV082_D2_HERO#1', attacker=attacker or fighter(),
        starting_resources=HeroResourceState(remaining_might=3), **kwargs,
    )


def test_no_might_retains_exact_charge_baselines():
    r = evidence()
    assert r.enhanced_uncharged == r.baseline_uncharged
    assert r.enhanced_charged == r.baseline_charged
    assert r.enhanced_cavalry_eligible == r.baseline_cavalry_eligible
    assert r.evidence_status == 'no_might_allocated_baseline_only'


def test_verified_strike_improves_fight_three_against_fight_four():
    r = evidence(heroic_strike=declaration())
    assert r.enhanced_uncharged > r.baseline_uncharged
    assert r.allocation.heroic_strike_reserved == 1
    assert r.allocation.remaining_might == 2
    assert r.dashboard_score is None and r.scenario_score is None


def test_might_strategy_improves_duel_without_heroic_strike():
    r = evidence(duel_might_budget=1,
                 duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)
    assert r.enhanced_uncharged > r.baseline_uncharged
    assert r.allocation.duel_might_reserved == 1


def test_strike_and_duel_might_use_distinct_reserved_points():
    r = evidence(heroic_strike=declaration(), duel_might_budget=1,
                 duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)
    assert r.allocation.remaining_might == 1
    assert r.enhanced_uncharged >= r.baseline_uncharged


def test_unauthorised_strike_cannot_produce_probability():
    with pytest.raises(ValueError, match='unverified_opportunity'):
        evidence(heroic_strike=declaration(check=CommandCheck.UNKNOWN))


def test_unowned_strike_cannot_produce_probability():
    with pytest.raises(ValueError, match='not on this model profile'):
        evidence(attacker=fighter(strike=False), heroic_strike=declaration())


def test_heroic_combat_is_not_an_offence_bonus():
    with pytest.raises(ValueError, match='Only Heroic Strike'):
        evidence(heroic_strike=declaration(action='HEROIC_COMBAT'))


def test_overspending_might_is_rejected():
    with pytest.raises(ValueError, match='Cannot spend more Might'):
        evidence(heroic_strike=declaration(), duel_might_budget=3,
                 duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)


def test_explicit_two_handed_weapon_is_preserved_in_enhanced_state():
    p = fighter(two_handed=True)
    chosen = MeleeWeaponSelection('WG_TWO_HANDED_WEAPON')
    r = evidence(attacker=p, attacker_selection=chosen, heroic_strike=declaration())
    assert r.evidence_status == 'verified_conditional_probability_not_calibrated'
    assert r.enhanced_uncharged > r.baseline_uncharged


def test_trapped_state_changes_strikes_but_not_might_reservation():
    a = evidence(heroic_strike=declaration(), defender_trapped=False)
    b = evidence(heroic_strike=declaration(), defender_trapped=True)
    assert b.baseline_uncharged > a.baseline_uncharged
    assert b.enhanced_uncharged > a.enhanced_uncharged
    assert b.allocation.remaining_might == a.allocation.remaining_might


def test_unknown_charge_probability_remains_unweighted():
    r = evidence(heroic_strike=declaration())
    assert r.weighted_baseline is None
    assert r.weighted_enhanced is None


def test_known_charge_probabilities_generate_weighted_pair():
    r = evidence(heroic_strike=declaration(), charge_probability=0.5,
                 cavalry_eligibility_probability=0.5)
    assert r.weighted_baseline is not None
    assert r.weighted_enhanced is not None
    assert r.weighted_enhanced >= r.weighted_baseline
