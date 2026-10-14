from fractions import Fraction as F
import pytest

from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import (
    reconcile_cross_method_resources, DeclaredMethodSpend, HeroHuntingMethod,
)
from hero_hunting_might_will_defence import DefenceResources as S, DefencePolicy as P, VerifiedWillProtection as W
from hero_hunting_unified_defence import UnifiedDefenceEvent as E, evaluate_unified_defence as evaluate


def budget(might=0,will=0,fate=0,spends=()):
    return reconcile_cross_method_resources(
        {"hero":HeroResourceState(might,will,fate)},tuple(spends))


def event(name, p=F(1), policy=None, target="hero"):
    return E(name,target,"2024 MESBG verified attack",
             (lambda state:p), policy or P())


def run(state,events,ledger=None):
    return evaluate("hero",state,tuple(events),ledger or budget(state.might,state.will,state.fate))


def test_empty_events_preserve_all_resources():
    r=run(S(2,2,1,3),())
    assert r.final_states=={S(2,2,1,3):F(1)}
    assert r.elimination_probability==0


def test_might_aware_fate_and_next_attack():
    r=run(S(1,2,0,1),(event("a",policy=P(1,1)),event("b",policy=P(1,1))))
    assert sum(r.final_states.values())==1
    assert all(s.might<=1 and s.fate<=2 for s in r.final_states)
    assert 0<r.elimination_probability<1


def test_two_guaranteed_wounds_one_fate_means_certain_elimination():
    r=run(S(1,1,0,0),(event("a",policy=P(1)),event("b",policy=P(1))))
    assert r.elimination_probability==1


def test_melee_then_spell_can_use_conditional_defence():
    e1=event("melee",F(1,2),P(1))
    e2=E("spell","hero","Chill Soul verified",
         lambda state:F(1) if state.fate==0 else F(0),P())
    r=run(S(1,1,0,0),(e1,e2))
    assert r.elimination_probability==F(1,2)


def test_will_requires_verified_rule():
    with pytest.raises(ValueError,match="verified"):
        P(use_will_if_no_fate_save=True)


def test_will_defence_tracks_depletion():
    policy=P(0,0,True,W("Verified Will-to-prevent rule",F(1,2)))
    r=run(S(1,0,1,0),(event("a",policy=policy),event("b",policy=policy)))
    assert r.elimination_probability==1


def test_prior_magic_will_spend_reduces_defensive_budget():
    spent=DeclaredMethodSpend("hero",HeroHuntingMethod.MAGIC_CAST,will=1)
    led=budget(will=2,spends=(spent,))
    assert run(S(1,0,1,0),(),led).final_states=={S(1,0,1,0):F(1)}


def test_cannot_ignore_prior_magic_will_spend():
    spent=DeclaredMethodSpend("hero",HeroHuntingMethod.MAGIC_CAST,will=1)
    with pytest.raises(ValueError,match="match E2"):
        run(S(1,0,2,0),(),budget(will=2,spends=(spent,)))


def test_cannot_ignore_prior_combat_might_spend():
    spent=DeclaredMethodSpend("hero",HeroHuntingMethod.MELEE,might=1)
    with pytest.raises(ValueError,match="match E2"):
        run(S(1,0,0,2),(),budget(might=2,spends=(spent,)))


def test_cannot_ignore_prior_fate_spend():
    spent=DeclaredMethodSpend("hero",HeroHuntingMethod.DEFENCE,fate=1)
    with pytest.raises(ValueError,match="match E2"):
        run(S(1,2,0,0),(),budget(fate=2,spends=(spent,)))


def test_missing_defender_budget_rejected():
    led=reconcile_cross_method_resources({"other":HeroResourceState(0,0,0)},())
    with pytest.raises(ValueError,match="one E2"):
        run(S(1,0,0,0),(),led)


def test_target_mismatch_rejected():
    with pytest.raises(ValueError,match="mismatch"):
        run(S(1,0,0,0),(event("a",target="other"),))


def test_duplicate_events_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        run(S(1,0,0,0),(event("a"),event("a")))


def test_unsupported_probability_rejected():
    with pytest.raises(ValueError,match="probability"):
        run(S(1,0,0,0),(event("a",F(2)),))


def test_no_fate_is_not_automatically_given_free_saves():
    r=run(S(1,0,0,0), (event("a",policy=P(3,3)),))
    assert r.elimination_probability==1


def test_dead_target_is_absorbing():
    r=run(S(1,0,0,0),(event("a"),event("b")))
    assert r.final_states=={S(0,0,0,0):F(1)}


def test_mixed_state_survival_and_elimination_totals_one():
    r=run(S(1,1,0,0),(event("a",F(1,2),P(1)),))
    assert r.elimination_probability==F(1,4)
    assert r.survival_probability==F(3,4)


def test_does_not_create_dashboard_or_scenario_score():
    r=run(S(1,0,0,0),())
    assert r.dashboard_score is None and r.scenario_score is None
