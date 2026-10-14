from fractions import Fraction as F
import pytest
from hero_hunting_might_will_defence import (
    DefenceResources as S, DefencePolicy as P, VerifiedWillProtection as W,
    defended_wound_distribution as resolve, evaluate_defended_sequence as run,
)

def test_fate_without_might_is_half_save():
    assert resolve(S(1,1,0,0),F(1),P(1))=={S(1,0,0,0):F(1,2),S(0,0,0,0):F(1,2)}

def test_one_might_improves_three_only():
    assert resolve(S(1,1,0,1),F(1),P(1,1))=={
        S(1,0,0,1):F(1,2),S(1,0,0,0):F(1,6),S(0,0,0,1):F(1,3)}

def test_two_might_improves_two_and_three():
    r=resolve(S(1,1,0,2),F(1),P(1,2))
    assert sum(v for s,v in r.items() if s.wounds==1)==F(5,6)

def test_three_might_guarantees_fate_save():
    r=resolve(S(1,1,0,3),F(1),P(1,3))
    assert sum(v for s,v in r.items() if s.wounds==0)==0

def test_might_preserved_when_fate_roll_succeeds_naturally():
    r=resolve(S(1,1,0,2),F(1),P(1,2))
    assert r[S(1,0,0,2)]==F(1,2)

def test_no_wound_consumes_nothing():
    assert resolve(S(1,1,1,2),F(0),P(1,2))=={S(1,1,1,2):F(1)}

def test_declined_fate_applies_wound():
    assert resolve(S(1,1,0,3),F(1),P(0,3))=={S(0,1,0,3):F(1)}

def test_might_cap_not_available():
    assert resolve(S(1,1,0,2),F(1),P(1,0))=={
        S(1,0,0,2):F(1,2),S(0,0,0,2):F(1,2)}

def test_second_fate_attempt_follows_first_failure():
    r=resolve(S(1,2,0,0),F(1),P(2))
    assert sum(v for s,v in r.items() if s.wounds==0)==F(1,4)
    assert sum(r.values())==1

def test_second_event_sees_consumed_might():
    r=run(S(1,2,0,1),(("first",F(1),P(1,1)),("second",F(1),P(1,1))))
    assert sum(r.values())==1
    assert all(s.might<=1 for s in r)

def test_will_protection_rejected_without_verified_rule():
    with pytest.raises(ValueError,match="verified"):
        P(use_will_if_no_fate_save=True)

def test_verified_will_consumed_on_both_outcomes():
    rule=W("2024 verified profile rule",F(1,3))
    assert resolve(S(1,0,1,0),F(1),P(use_will_if_no_fate_save=True,verified_will_protection=rule))=={
        S(1,0,0,0):F(1,3),S(0,0,0,0):F(2,3)}

def test_will_unavailable_results_in_wound():
    rule=W("Verified rule",F(1,2))
    assert resolve(S(1,0,0,0),F(1),P(use_will_if_no_fate_save=True,verified_will_protection=rule))=={S(0,0,0,0):F(1)}

def test_will_used_after_failed_fate_when_declared():
    rule=W("Verified sequence",F(1,2))
    r=resolve(S(1,1,1,0),F(1),P(1,0,True,rule))
    assert sum(v for s,v in r.items() if s.wounds==1)==F(3,4)

def test_exhausted_will_in_next_event():
    rule=W("Verified rule",F(1,2))
    pol=P(0,0,True,rule)
    r=run(S(1,0,1,0),(("a",F(1),pol),("b",F(1),pol)))
    assert sum(v for s,v in r.items() if s.wounds==0)==1

def test_cannot_overspend_might():
    assert all(s.might>=0 for s in resolve(S(1,2,0,1),F(1),P(2,3)))

def test_reject_bad_will_source():
    with pytest.raises(ValueError,match="source"):
        W("",F(1,2))

def test_reject_float_will_probability():
    with pytest.raises(ValueError,match="probability"):
        W("verified",0.5)

def test_reject_duplicate_events():
    with pytest.raises(ValueError,match="unique"):
        run(S(1,1,0,0),(("a",F(1),P()),("a",F(1),P())))

def test_eliminated_targets_absorb_later_events():
    r=run(S(1,0,0,0),(("a",F(1),P()),("b",F(1),P())))
    assert r=={S(0,0,0,0):F(1)}

def test_invalid_probability_rejected():
    with pytest.raises(ValueError,match="probability"):
        resolve(S(1,1,0,0),F(2),P())

def test_invalid_negative_might_rejected():
    with pytest.raises(ValueError):
        S(1,1,0,-1)
