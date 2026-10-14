from fractions import Fraction as F
import pytest
from hero_hunting_target_survival import (
    TargetSurvivalState as S, VerifiedTargetEvent as E, evaluate_target_survival as run,
)


def attack(eid, p, target='leader'):
    def transition(s):
        wounded = S(s.wounds - 1, s.fate, s.will)
        if wounded == s:
            return {s: F(1)}
        return {s: F(1)-p, wounded: p}
    return E(eid, target, 'verified conditional damage', transition)


def test_empty_sequence_preserves_target():
    r=run('leader', S(2,1,1), ())
    assert r.elimination_probability == 0 and r.survival_probability == 1


def test_single_one_wound_elimination():
    assert run('leader', S(1), (attack('a',F(1,2)),)).elimination_probability == F(1,2)


def test_two_one_wound_attacks_do_not_add_probabilities():
    assert run('leader', S(1), (attack('a',F(1,2)),attack('b',F(1,2)))).elimination_probability == F(3,4)


def test_two_wound_hero_requires_two_hits():
    r=run('leader', S(2), (attack('a',F(1,2)),attack('b',F(1,2))))
    assert r.elimination_probability == F(1,4)


def test_conditional_fate_consumption_affects_later_events():
    def guarded(s):
        if s.fate:
            return {S(s.wounds,0,s.will):F(1)}
        return {S(s.wounds-1,0,s.will):F(1)}
    ev=lambda name:E(name,'leader','verified conditional fate',guarded)
    result=run('leader',S(1,1),(ev('one'),ev('two')))
    assert result.elimination_probability == 1


def test_conditional_will_spend_affects_next_event():
    def resisted(s):
        return {S(s.wounds,s.fate,0):F(1)} if s.will else {S(0,s.fate,0):F(1)}
    ev=lambda name:E(name,'leader','verified resistance resolution',resisted)
    assert run('leader',S(1,0,1),(ev('one'),ev('two'))).elimination_probability == 1


def test_dead_state_is_absorbing_and_transition_not_invoked():
    def forbidden(_):
        raise AssertionError('dead target must not be attacked')
    r=run('leader',S(1),(attack('one',F(1)),E('two','leader','source',forbidden)))
    assert r.elimination_probability == 1


def test_reject_duplicate_event_ids():
    with pytest.raises(ValueError,match='Duplicate'):
        run('leader',S(1),(attack('a',F(1)),attack('a',F(1))))


def test_reject_other_target():
    with pytest.raises(ValueError,match='target mismatch'):
        run('leader',S(1),(attack('a',F(1),'other'),))


def test_missing_condition_is_not_automatically_inferred():
    with pytest.raises(ValueError,match='Missing conditional'):
        run('leader',S(1),(E('a','leader','source',lambda _: {}),))


def test_non_normalized_probability_rejected():
    with pytest.raises(ValueError,match='total one'):
        run('leader',S(1),(E('a','leader','source',lambda s: {s:F(1,3)}),))


def test_fraction_only_probabilities():
    with pytest.raises(TypeError,match='Fractions'):
        run('leader',S(1),(E('a','leader','source',lambda s: {s:1.0}),))


def test_reject_unverified_recovery():
    with pytest.raises(ValueError,match='recovery'):
        run('leader',S(1),(E('a','leader','source',lambda s:{S(2):F(1)}),))


def test_reject_initial_dead_target():
    with pytest.raises(ValueError,match='living'):
        run('leader',S(0),())


def test_reject_negative_state():
    with pytest.raises(ValueError,match='negative'):
        S(-1)


def test_reject_undocumented_source():
    with pytest.raises(ValueError,match='documented'):
        E('a','leader','',lambda s:{s:F(1)})


def test_preserves_exact_distribution():
    r=run('leader',S(1),(attack('a',F(1,3)),))
    assert r.surviving_states[S(1)] == F(2,3)
    assert r.surviving_states[S(0)] == F(1,3)
    assert r.dashboard_score is None and r.scenario_score is None
