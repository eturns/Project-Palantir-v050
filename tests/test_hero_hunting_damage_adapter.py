from fractions import Fraction
import pytest

from hero_hunting_evidence_consistency import MethodEvidence, EvidenceStatus, OutcomeType
from hero_hunting_resource_adapter import HeroHuntingMethod
from hero_hunting_target_survival import TargetSurvivalState as State
from hero_hunting_damage_adapter import (
    VerifiedDamageEvent, evaluate_damage_event_sequence,
    verified_unprevented_single_wound,
)


def observation(eid="a", method=HeroHuntingMethod.MELEE,
                status=EvidenceStatus.VERIFIED, outcome=OutcomeType.ELIMINATION):
    return MethodEvidence(
        eid, eid, "attacker", "leader", method, outcome, status,
        Fraction(1, 2) if status is EvidenceStatus.VERIFIED else None,
        "Rules Manual 2024" if status is EvidenceStatus.VERIFIED else None,
    )


def single(eid="a", *, method=HeroHuntingMethod.MELEE, prob=Fraction(1,2)):
    return verified_unprevented_single_wound(
        observation(eid, method),
        conditional_wound_probability=lambda state: prob,
        no_prevention_verified=True,
        transition_rule_source="Rules Manual 2024; defence excluded by verified context",
    )


def run(events, *, wounds=2, fate=0, will=0):
    return evaluate_damage_event_sequence("leader",State(wounds,fate,will),tuple(events))


def test_two_hits_need_both_for_two_wound_target():
    assert run([single("a"),single("b")]).elimination_probability == Fraction(1,4)


def test_two_hits_one_wound_target():
    assert run([single("a"),single("b")],wounds=1).elimination_probability == Fraction(3,4)


def test_melee_shooting_magic_event_order_retained():
    ev=[single("a"),single("b",method=HeroHuntingMethod.SHOOTING),
        single("c",method=HeroHuntingMethod.MAGIC_CAST)]
    result=run(ev,wounds=2)
    assert result.event_ids == ("a","b","c")
    assert result.elimination_probability == Fraction(1,2)


def test_state_conditioned_second_hit():
    first=single("a")
    second=verified_unprevented_single_wound(
        observation("b"),
        conditional_wound_probability=lambda s: Fraction(1,1) if s.wounds == 1 else Fraction(0),
        no_prevention_verified=True,
        transition_rule_source="Verified conditional rule",
    )
    assert run([first,second]).elimination_probability == Fraction(1,2)


def test_resource_spending_persists_between_events():
    first=VerifiedDamageEvent(
        observation("a"),
        lambda s: {State(s.wounds,s.fate-1,s.will):Fraction(1)},
        "Verified Fate expenditure",
    )
    second=VerifiedDamageEvent(
        observation("b"),
        lambda s: {State(s.wounds-1,s.fate,s.will):Fraction(1)} if s.fate == 0
        else {s:Fraction(1)},
        "Verified state-conditional attack",
    )
    result=run((first,second),wounds=1,fate=1)
    assert result.elimination_probability == 1
    assert State(0,0,0) in result.surviving_states


def test_zero_wounds_absorb_later_damage():
    result=run((single("a",prob=Fraction(1)),single("b",prob=Fraction(1))),wounds=1)
    assert result.elimination_probability == 1


def test_observation_probability_not_used_as_damage_probability():
    result=run((single("a",prob=Fraction(1,3)),),wounds=1)
    assert result.elimination_probability == Fraction(1,3)


def test_requires_explicit_no_prevention_validation():
    with pytest.raises(ValueError,match="prevention"):
        verified_unprevented_single_wound(
            observation(),conditional_wound_probability=lambda _:Fraction(1,2),
            no_prevention_verified=False,transition_rule_source="Rule")


def test_reject_unverified_observation():
    with pytest.raises(ValueError,match="verified"):
        VerifiedDamageEvent(observation(status=EvidenceStatus.UNRESOLVED),
                            lambda s:{s:Fraction(1)},"Rule")


def test_reject_control_as_direct_damage():
    with pytest.raises(ValueError,match="elimination"):
        VerifiedDamageEvent(observation(outcome=OutcomeType.CONTROL),
                            lambda s:{s:Fraction(1)},"Rule")


def test_reject_undocumented_transition_source():
    with pytest.raises(ValueError,match="rule_source"):
        VerifiedDamageEvent(observation(),lambda s:{s:Fraction(1)}," ")


def test_reject_duplicate_event_identifiers():
    with pytest.raises(ValueError,match="Duplicate event_id"):
        run((single("a"),single("a")))


def test_reject_target_mismatch():
    with pytest.raises(ValueError,match="target mismatch"):
        evaluate_damage_event_sequence("other",State(1), (single("a"),))


def test_reject_missing_conditional_distribution():
    ev=VerifiedDamageEvent(observation(),lambda s:{}, "Rule")
    with pytest.raises(ValueError,match="Missing conditional"):
        run((ev,))


def test_reject_incorrect_transition_total():
    ev=VerifiedDamageEvent(observation(),lambda s:{s:Fraction(1,3)}, "Rule")
    with pytest.raises(ValueError,match="total one"):
        run((ev,))


def test_reject_illegal_resource_increase():
    ev=VerifiedDamageEvent(observation(),lambda s:{State(s.wounds,s.fate+1,s.will):Fraction(1)}, "Rule")
    with pytest.raises(ValueError,match="recovery"):
        run((ev,))


def test_reject_bad_probability_type():
    event=verified_unprevented_single_wound(
        observation(),conditional_wound_probability=lambda s:0.5,
        no_prevention_verified=True,transition_rule_source="Rule")
    with pytest.raises(TypeError,match="Fraction"):
        run((event,))


def test_no_effect_is_zero_elimination():
    assert run((),wounds=1).elimination_probability == 0
