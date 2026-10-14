from fractions import Fraction as F
import pytest

from hero_hunting_target_survival import TargetSurvivalState as State
from hero_hunting_stateful_defence import (
    VerifiedDefencePlan as Plan, StatefulDefendedWound as Event,
    single_wound_defence_transition as transition,
    evaluate_stateful_defended_wounds as evaluate,
)


def event(name, p=F(1), plan=None, eligible=True):
    return Event(name, "hero", "Verified 2024 one-wound attack",
                 lambda state:p, plan or Plan(), eligible)


def test_fate_save_consumes_fate():
    assert transition(State(1,1),F(1),Plan(spend_one_fate_if_wounded=True)) == {
        State(1,0):F(1,2), State(0,0):F(1,2)}


def test_failed_fate_consumes_fate():
    assert State(0,0) in transition(State(1,1),F(1),Plan(spend_one_fate_if_wounded=True))


def test_no_wound_no_fate_spent():
    assert transition(State(1,1),F(0),Plan(spend_one_fate_if_wounded=True)) == {State(1,1):F(1)}


def test_partial_wound_probability():
    result=transition(State(1,1),F(1,2),Plan(spend_one_fate_if_wounded=True))
    assert result[State(1,1)] == F(1,2)
    assert result[State(1,0)] == F(1,4)
    assert result[State(0,0)] == F(1,4)


def test_second_wound_sees_depleted_fate():
    result=evaluate("hero",State(1,1),(event("a",plan=Plan(True)),event("b",plan=Plan(True))))
    assert result.elimination_probability == F(1)


def test_second_wound_keeps_remaining_wounds():
    result=evaluate("hero",State(2,1),(event("a",plan=Plan(True)),event("b",plan=Plan(True))))
    assert result.elimination_probability == F(1,2)


def test_two_wounds_no_defence():
    result=evaluate("hero",State(2,0),(event("a",F(1,2)),event("b",F(1,2))))
    assert result.elimination_probability == F(1,4)


def test_no_fate_falls_back_to_wound():
    assert transition(State(1,0),F(1),Plan(True)) == {State(0,0):F(1)}


def test_will_protection_requires_verification():
    with pytest.raises(ValueError,match="verified"):
        Plan(spend_one_will_if_wounded=True)


def test_will_defence_consumes_will_both_branches():
    p=Plan(spend_one_will_if_wounded=True, will_save_probability=F(1,3),
           will_rule_source="Verified profile-specific protection")
    assert transition(State(1,0,1),F(1),p) == {
        State(1,0,0):F(1,3),State(0,0,0):F(2,3)}


def test_exhausted_will_cannot_protect():
    p=Plan(spend_one_will_if_wounded=True,will_save_probability=F(1,2),
           will_rule_source="Verified exception")
    assert transition(State(1,0,0),F(1),p) == {State(0,0,0):F(1)}


def test_will_then_second_wound_has_no_will():
    p=Plan(spend_one_will_if_wounded=True,will_save_probability=F(1,2),
           will_rule_source="Verified exception")
    result=evaluate("hero",State(1,0,1),(event("a",plan=p),event("b",plan=p)))
    assert result.elimination_probability == F(1)


def test_stacking_two_saves_rejected():
    with pytest.raises(ValueError,match="stack"):
        Plan(True,True,F(1,2),"Rule")


def test_defence_not_allowed_for_ineligible_attack():
    with pytest.raises(ValueError,match="cannot apply"):
        event("a",plan=Plan(True),eligible=False)


def test_invalid_probability_rejected():
    with pytest.raises(ValueError,match="out of range"):
        transition(State(1),F(2),Plan())


def test_fraction_required():
    with pytest.raises(TypeError,match="Fraction"):
        transition(State(1),0.5,Plan())


def test_no_resurrection_after_elimination():
    result=evaluate("hero",State(1),(event("a"),event("b")))
    assert result.elimination_probability == 1


def test_conditional_probability_by_remaining_fate():
    conditional=Event("a","hero","Verified rule",
                      lambda s:F(1) if s.fate == 0 else F(0),
                      Plan())
    result=evaluate("hero",State(1,1),(conditional,))
    assert result.elimination_probability == 0


def test_wrong_target_rejected():
    with pytest.raises(ValueError,match="mismatch"):
        evaluate("other",State(1),(event("a"),))


def test_duplicate_event_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        evaluate("hero",State(1),(event("a"),event("a")))


def test_will_rule_metadata_disallowed_when_not_spending():
    with pytest.raises(ValueError,match="Unspent"):
        Plan(will_rule_source="not used")
