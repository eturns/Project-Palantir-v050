"""DEV-082-A2-3 consolidated diagnostic acceptance.
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
from offence_charge_state_evidence import calculate_charge_state_offence_evidence
from offence_mechanical_contract import calculate_mechanical_offence_contract as contract
from profiles import Profile
from wargear import Wargear


def hero(*, strike=True, weapon=False):
    p = Profile(
        id='DEV082_A3', name='Mechanical Offence contract hero', points=80,
        movement=6, fight=3, shooting='4+', strength=4, defence=5,
        attacks=2, wounds=2, courage='4+', intelligence='4+',
        might=3, will=0, fate=0, max_in_army=1,
    )
    if strike:
        p.heroic_actions.append(HeroicAction(
            id='HEROIC_STRIKE', name='Heroic Strike', category=RuleCategory.OFFENCE))
    if weapon:
        p.default_wargear.append(Wargear(id='WG_TWO_HANDED_WEAPON', name='Two-handed Weapon'))
    return ConfiguredProfile(p)


def strike_declaration():
    return CommandActionDeclaration(
        event_id='dev082-a3-strike', actor_id='DEV082_A3#1',
        heroic_action_id='HEROIC_STRIKE', turn=1,
        timing_legal=CommandCheck.VERIFIED_TRUE,
        activation_legal=CommandCheck.VERIFIED_TRUE,
        battlefield_legal=CommandCheck.VERIFIED_TRUE,
        might_cost=1,
    )


def resources():
    return dict(actor_id='DEV082_A3#1', starting_resources=HeroResourceState(remaining_might=3))


def test_baseline_only_matches_existing_diagnostic_exactly():
    h = hero()
    result = contract(h)
    existing = calculate_charge_state_offence_evidence(h)
    assert result.baseline == existing
    assert result.heroic is None
    assert result.weighted_baseline is None
    assert result.weighted_enhanced is None


def test_unknown_context_declared_not_guessed():
    result = contract(hero())
    assert set(result.unresolved_context) == {
        'weapon_choice_implicit', 'trap_state_unknown_untrapped_reference',
        'target_keywords_unspecified', 'charge_probability_unknown',
        'cavalry_eligibility_probability_unknown',
    }
    assert result.dashboard_score is None and result.scenario_score is None
    assert result.integration_status == 'diagnostic_only_not_connected_to_production'


def test_explicit_context_has_no_unknown_flags():
    h = hero(weapon=True)
    result = contract(
        h, attacker_selection=MeleeWeaponSelection('WG_TWO_HANDED_WEAPON'),
        defender_trapped=False, target_keywords=(),
        charge_probability=0.5, cavalry_eligibility_probability=0.25,
    )
    assert result.unresolved_context == ()
    assert result.weighted_baseline is not None
    assert result.weighted_enhanced is None


def test_authorised_strike_preserves_baseline_and_improves_conditional_duel():
    h = hero()
    result = contract(h, **resources(), heroic_strike=strike_declaration())
    assert result.heroic is not None
    assert result.heroic.allocation.heroic_strike_reserved == 1
    assert result.heroic.allocation.remaining_might == 2
    assert result.heroic.enhanced_uncharged > result.uncharged
    assert result.baseline == calculate_charge_state_offence_evidence(h)
    assert result.evidence_status == 'conditional_evidence_not_calibrated'


def test_duel_might_plan_is_separate_from_strike():
    result = contract(
        hero(), **resources(), heroic_strike=strike_declaration(),
        duel_might_budget=1, duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )
    assert result.heroic.allocation.heroic_strike_reserved == 1
    assert result.heroic.allocation.duel_might_reserved == 1
    assert result.heroic.allocation.remaining_might == 1


def test_actor_without_spending_keeps_exact_baseline():
    result = contract(hero(), **resources())
    assert result.heroic.enhanced_uncharged == result.uncharged
    assert result.evidence_status == 'baseline_only_not_calibrated'


def test_known_probability_gives_conditional_weighted_pair():
    result = contract(
        hero(), **resources(), heroic_strike=strike_declaration(),
        charge_probability=0.5, cavalry_eligibility_probability=0.5,
    )
    assert result.weighted_baseline is not None
    assert result.weighted_enhanced is not None
    assert result.weighted_enhanced > result.weighted_baseline


@pytest.mark.parametrize('kwargs', [
    {'actor_id': 'DEV082_A3#1'},
    {'starting_resources': HeroResourceState(remaining_might=3)},
    {'duel_might_budget': 1, 'duel_might_strategy': DuelMightStrategy.MAXIMISE_ROLL},
])
def test_incomplete_resource_context_rejected(kwargs):
    with pytest.raises(ValueError, match='actor_id and starting_resources|Might allocation requires'):
        contract(hero(), **kwargs)


def test_heroic_combat_never_allowed_in_offence():
    declaration = CommandActionDeclaration(
        event_id='combat', actor_id='DEV082_A3#1', heroic_action_id='HEROIC_COMBAT',
        turn=1, timing_legal=CommandCheck.VERIFIED_TRUE,
        activation_legal=CommandCheck.VERIFIED_TRUE,
        battlefield_legal=CommandCheck.VERIFIED_TRUE,
    )
    with pytest.raises(ValueError, match='Only Heroic Strike'):
        contract(hero(), **resources(), heroic_strike=declaration)


def test_insufficient_might_propagates_failure():
    with pytest.raises(ValueError, match='Cannot spend more Might'):
        contract(
            hero(), actor_id='DEV082_A3#1',
            starting_resources=HeroResourceState(remaining_might=1),
            heroic_strike=strike_declaration(), duel_might_budget=1,
            duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
        )
