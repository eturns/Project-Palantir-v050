"""DEV-082-A3-2H-3 joint Duel/wound read-only acceptance tests."""
import sys
import types
from types import SimpleNamespace as S
from fractions import Fraction
import pytest

from offence_joint_support_wounds import (
    combine_independent_strike_failures, calculate_explicit_joint_support_kill,
)
from offence_explicit_support_combat import ExplicitSupportContext


def fake_config(pid, *, strength=4, attacks=1, rules=(), gear=("WG_HAND_WEAPON",)):
    p = S(id=pid, fight=4, strength=strength, attacks=attacks,
          base_size_mm=25)
    return S(profile=p, effective_fight=4, effective_strength=strength,
             effective_attacks=attacks, effective_base_size_mm=25,
             effective_model_types={"INFANTRY"},
             effective_special_rules=[S(rule=S(id=x)) for x in rules],
             effective_wargear=[S(id=x) for x in gear])


@pytest.fixture
def standins(monkeypatch):
    benchmark = types.ModuleType("combat_benchmark")
    benchmark.DEFAULT_COMBAT_BENCHMARK = S(fight=4, attacks=1,
                                          strength=4, defence=6, wounds=1)
    monkeypatch.setitem(sys.modules, "combat_benchmark", benchmark)
    profiles = types.ModuleType("profiles")
    profiles.Profile = lambda **kw: S(**kw)
    monkeypatch.setitem(sys.modules, "profiles", profiles)
    configured = types.ModuleType("configured_profile")
    configured.ConfiguredProfile = lambda *, profile: S(profile=profile)
    monkeypatch.setitem(sys.modules, "configured_profile", configured)
    wound = types.ModuleType("wound_context")
    wound.WoundContext = lambda **kw: S(**kw)
    monkeypatch.setitem(sys.modules, "wound_context", wound)
    attack = types.ModuleType("wound_attack_type")
    attack.WoundAttackType = S(STRIKE="STRIKE")
    monkeypatch.setitem(sys.modules, "wound_attack_type", attack)
    return benchmark.DEFAULT_COMBAT_BENCHMARK


def fake_duel(fighter, supporter, **kwargs):
    return {
        "status": "conditional_duel_calculated",
        "fighter_strikes_if_win": fighter.effective_attacks,
        "supporter_strikes_if_win": 1,
        "combined_duel_win_probability": 0.5,
        "supporter_not_independent_combat": True,
        "model_allocation": {"fighters": ["F"], "supporters": ["S"],
                             "independent_model_scores_added": False},
        "production_scoring_changed": False,
    }


def fake_wound(attacker, defender, *, context):
    return Fraction(1, 3) if attacker.profile.id == "F" else Fraction(1, 2)


def run(f=None, s=None, **kwargs):
    deps = {"duel_calculator": fake_duel, "wound_calculator": fake_wound}
    deps.update(kwargs)
    return calculate_explicit_joint_support_kill(
        f or fake_config("F"), s or fake_config("S", gear=("WG_SPEAR",)),
        fighter_id="F", supporter_id="S",
        context=ExplicitSupportContext.conditional_example(),
        **deps,
    )


def test_two_different_wound_probabilities(standins):
    r=run()
    assert r["fighter_wound_probability_per_strike"] == pytest.approx(1/3)
    assert r["supporter_wound_probability_per_strike"] == pytest.approx(1/2)


def test_combined_success_exact_reference(standins):
    r=run()
    # P(Duel)=1/2, P(any wound | win)=1-(2/3)(1/2)=2/3
    assert r["probability_at_least_one_wound_given_duel_win"] == pytest.approx(2/3)
    assert r["combined_kill_probability"] == pytest.approx(1/3)


def test_only_one_joint_combat_and_not_two_solo_scores(standins):
    r=run()
    assert r["model_allocation"]["independent_model_scores_added"] is False
    assert r["supporter_not_independent_combat"] is True


def test_fighter_attack_count_and_one_support_strike(standins):
    r=run(f=fake_config("F", attacks=2))
    assert r["strike_distribution"]["total_eligible_strikes"] == 3
    assert r["strike_distribution"]["supporter_eligible_strikes"] == 1
    assert r["combined_kill_probability"] == pytest.approx(
        0.5*(1-(2/3)**2*(1/2))
    )


def test_no_scoring_or_calibration(standins):
    r=run()
    assert r["candidate_raw_density"] is None
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False
    assert r["dashboard_score"] is None


@pytest.mark.parametrize("win, probs, expectation", [
    (0., [1., 1.], 0.),
    (1., [0., 0.], 0.),
    (1., [1., 0.], 1.),
    (.5, [.5, .5], .375),
    (1., [.25, .5], .625),
])
def test_probability_independent_reference(win, probs, expectation):
    assert combine_independent_strike_failures(win, probs) == pytest.approx(expectation)


@pytest.mark.parametrize("win, probs", [
    (-.1, [.5]), (1.1, [.5]),
    (float("nan"), [.5]), (float("inf"), [.5]),
    (.5, []), (.5, [-.1]), (.5, [1.1]),
    (.5, [float("nan")]), (.5, [float("inf")]),
])
def test_bad_probability_rejected(win, probs):
    with pytest.raises(ValueError):
        combine_independent_strike_failures(win, probs)


def test_unmodelled_wound_rule_rejected(standins):
    with pytest.raises(ValueError, match="Unmodelled"):
        run(f=fake_config("F", rules=("BACKSTABBERS",)))


def test_two_handed_option_rejected(standins):
    with pytest.raises(ValueError, match="Two-handed"):
        run(f=fake_config("F", gear=("WG_TWO_HANDED_WEAPON",)))


def test_multiple_wound_benchmark_rejected(standins):
    bench = S(fight=4, attacks=1, strength=4, defence=6, wounds=2)
    with pytest.raises(ValueError, match="single-wound"):
        run(benchmark=bench)


def test_invalid_duel_contract_rejected(standins):
    def bad(*args, **kwargs):
        result=fake_duel(*args, **kwargs)
        result["supporter_not_independent_combat"]=False
        return result
    with pytest.raises(ValueError, match="independent"):
        calculate_explicit_joint_support_kill(
            fake_config("F"), fake_config("S"),
            fighter_id="F", supporter_id="S",
            context=ExplicitSupportContext.conditional_example(),
            duel_calculator=bad, wound_calculator=fake_wound,
        )


def test_no_implicit_trap_charge_might(standins):
    r=run()
    assert r["combat_assumptions"]["defender_trapped"] is False
    assert r["combat_assumptions"]["attacker_charged"] is False
    assert r["combat_assumptions"]["might_spent"] == 0


def test_supporter_is_individually_evaluated(standins):
    seen=[]
    def wound(attacker, defender, *, context):
        seen.append(attacker.profile.id)
        return .5
    run(wound_calculator=wound)
    assert seen == ["F", "S"]
