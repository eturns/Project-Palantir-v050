from fractions import Fraction
import pytest
from hero_hunting_target_survival import TargetSurvivalState
from hero_hunting_damage_adapter import evaluate_damage_event_sequence
from hero_hunting_mechanical_transitions import (from_shooting_evidence, from_melee_single_strike, from_chill_soul)
from hero_hunting_melee import HeroHuntingMeleeEvidence
from hero_hunting_shooting import ShootingHeroHuntingEvidence
from hero_hunting_magic import MagicHeroHuntingEvidence


def shooting(shots=2, p=Fraction(1,2)):
    return ShootingHeroHuntingEvidence(shots,p,shots*p,Fraction(0))


def melee(duel=.5, wound=.5, strike_wounds=1):
    return HeroHuntingMeleeEvidence(duel,wound,duel*wound,duel*wound,strike_wounds)


def magic(spell='CHILL_SOUL',p=.5):
    return MagicHeroHuntingEvidence(spell,.5,p,1,0,1,0)


def volley(ev=None):
    return from_shooting_evidence(evidence=ev or shooting(),actor_id='archer',
        target_id='leader',event_prefix='volley1',no_wound_prevention_verified=True)


def strike(ev=None, **kw):
    return from_melee_single_strike(evidence=ev or melee(), actor_id='warrior',
        target_id='leader', event_id='combat1', exactly_one_strike_verified=True,
        no_wound_prevention_verified=True,**kw)


def spell(ev=None):
    return from_chill_soul(evidence=ev or magic(), actor_id='wizard',
        target_id='leader', event_id='spell1',no_wound_prevention_verified=True)


def resolve(events,wounds=1):
    return evaluate_damage_event_sequence('leader',TargetSurvivalState(wounds),tuple(events))


def test_shooting_two_shots_one_wound():
    assert resolve(volley()).elimination_probability == Fraction(3,4)


def test_shooting_two_shots_two_wounds():
    assert resolve(volley(),wounds=2).elimination_probability == Fraction(1,4)


def test_actual_shot_probability_used_not_elimination():
    assert resolve(volley(shooting(1,Fraction(1,3)))).elimination_probability == Fraction(1,3)


def test_single_melee_strike_duel_conditioned():
    assert resolve([strike()]).elimination_probability == Fraction(1,4)


def test_one_wound_magic():
    assert resolve([spell()]).elimination_probability == Fraction(1,2)


def test_three_methods_sequential_two_wounds():
    e=(strike(),)+volley(shooting(1,Fraction(1,2)))+(spell(),)
    assert resolve(e,wounds=2).elimination_probability == Fraction(3,8)


def test_reject_melee_multi_strike():
    with pytest.raises(ValueError, match='exactly one strike'):
        from_melee_single_strike(evidence=melee(),actor_id='a',target_id='leader',
            event_id='a',exactly_one_strike_verified=False,no_wound_prevention_verified=True)


def test_reject_melee_more_than_one_wound():
    with pytest.raises(ValueError, match='multiple wounds'):
        strike(melee(strike_wounds=2))


def test_reject_shooting_unverified_defence():
    with pytest.raises(ValueError,match='prevention'):
        from_shooting_evidence(evidence=shooting(),actor_id='a',target_id='leader',
            event_prefix='e',no_wound_prevention_verified=False)


def test_reject_wrong_spell():
    with pytest.raises(ValueError,match='Chill Soul'):
        spell(magic('WITHER'))


def test_reject_magic_unverified_defence():
    with pytest.raises(ValueError,match='prevention'):
        from_chill_soul(evidence=magic(),actor_id='a',target_id='leader',event_id='e',
            no_wound_prevention_verified=False)


def test_shot_ids_distinct():
    assert len({e.observation.event_id for e in volley()})==2


def test_reject_bad_shot_count():
    with pytest.raises(ValueError,match='shot count'):
        volley(shooting(0))


def test_reject_bad_melee_probability():
    with pytest.raises(ValueError,match='range'):
        strike(melee(duel=1.5))


def test_caster_not_hardcoded():
    e=from_chill_soul(evidence=magic(),actor_id='different_wizard',
          target_id='leader',event_id='different_cast',no_wound_prevention_verified=True)
    assert e.observation.actor_id=='different_wizard'
