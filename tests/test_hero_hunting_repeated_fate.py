from fractions import Fraction as F
import pytest
from hero_hunting_target_survival import TargetSurvivalState as S
from hero_hunting_repeated_fate import FateAttemptPolicy as Policy, repeated_fate_transition as tr, RepeatedFateWoundEvent as Event, evaluate_repeated_fate_events as seq

def ev(name,p=F(1),n=2):
    return Event(name,"hero","2024 MESBG Fate rules",p,Policy(n))

def test_two_fate_attempts_full_damage():
    assert tr(S(1,2),F(1),Policy(2)) == {
        S(1,1):F(1,2),S(1,0):F(1,4),S(0,0):F(1,4)}

def test_one_fate_attempt_only():
    assert tr(S(1,2),F(1),Policy(1)) == {S(1,1):F(1,2),S(0,1):F(1,2)}

def test_zero_fate_wound_taken():
    assert tr(S(1,0),F(1),Policy(9)) == {S(0,0):F(1)}

def test_decline_fate_wound_taken_without_spend():
    assert tr(S(1,2),F(1),Policy(0)) == {S(0,2):F(1)}

def test_no_wound_means_no_fate_spent():
    assert tr(S(1,2),F(0),Policy(2)) == {S(1,2):F(1)}

def test_partial_damage_preserves_no_hit_branch():
    r=tr(S(1,2),F(1,2),Policy(2))
    assert r[S(1,2)]==F(1,2)
    assert r[S(0,0)]==F(1,8)
    assert sum(r.values())==1

def test_fate_cap_limited_by_remaining_points():
    assert tr(S(1,1),F(1),Policy(9)) == {S(1,0):F(1,2),S(0,0):F(1,2)}

def test_will_remains_unchanged():
    assert all(s.will==3 for s in tr(S(1,2,3),F(1),Policy(2)))

def test_next_attack_sees_consumed_fate():
    r=seq("hero",S(1,2),(ev("a"),ev("b")))
    assert r.elimination_probability==F(3,4)

def test_three_automatic_wounds_overcome_two_fate():
    r=seq("hero",S(1,2),(ev("a"),ev("b"),ev("c")))
    assert r.elimination_probability==F(1)

def test_two_wound_target_one_attack_cannot_die():
    assert seq("hero",S(2,2),(ev("a"),)).elimination_probability==0

def test_duplicate_event_fails():
    with pytest.raises(ValueError,match="Duplicate"):
        seq("hero",S(1,2),(ev("a"),ev("a")))

def test_target_mismatch_fails():
    with pytest.raises(ValueError,match="mismatch"):
        seq("other",S(1,2),(ev("a"),))

def test_fraction_required():
    with pytest.raises(TypeError,match="Fraction"):
        tr(S(1,2),0.5,Policy(2))

def test_probability_above_one_rejected():
    with pytest.raises(ValueError,match="range"):
        tr(S(1,2),F(2),Policy(2))

def test_negative_cap_rejected():
    with pytest.raises(ValueError,match="negative"):
        Policy(-1)

def test_bool_cap_rejected():
    with pytest.raises(TypeError,match="integer"):
        Policy(True)

def test_invalid_state_rejected():
    with pytest.raises(ValueError,match="living"):
        tr(S(0,2),F(1),Policy(2))

def test_empty_events_no_elimination():
    assert seq("hero",S(1,2),()).elimination_probability==0
