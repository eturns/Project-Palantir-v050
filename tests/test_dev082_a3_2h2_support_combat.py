"""DEV-082-A3-2H-2 explicit standard spear support contract tests."""
import sys
import types
from dataclasses import replace
from types import SimpleNamespace as S
import pytest

from offence_explicit_support_combat import (
    ExplicitSupportContext, validate_explicit_spear_support,
    calculate_explicit_support_duel,
)


def configured(*, profile_id="A", gear=(), typ=("INFANTRY",), fight=4,
               effective_fight=None, base=25, effective_base=None,
               strength=4, attacks=1):
    profile = S(id=profile_id, fight=fight, base_size_mm=base,
                strength=strength, attacks=attacks)
    return S(profile=profile, effective_fight=fight if effective_fight is None else effective_fight,
             effective_base_size_mm=base if effective_base is None else effective_base,
             effective_strength=strength, effective_attacks=attacks,
             effective_model_types=set(typ),
             effective_wargear=[S(id=i) for i in gear])


def pair():
    return configured(profile_id="IH_FRONT"), configured(profile_id="IH_SUPPORT", gear=("WG_SPEAR",))


def context():
    return ExplicitSupportContext.conditional_example()


def test_supporter_gets_one_duel_die_and_one_strike():
    fighter, support = pair()
    r = validate_explicit_spear_support(fighter, support, context())
    assert r["supporter_duel_dice"] == 1
    assert r["supporter_strikes_if_win"] == 1
    assert r["supporter_strike_strength"] == 4


def test_supporters_fight_value_preserved():
    f, s = pair()
    s.effective_fight = 5
    s.profile.fight = 5
    assert validate_explicit_spear_support(f, s, context())["supporter_fight"] == 5


def test_rule_flags_do_not_auto_activate():
    assert all(getattr(context(), f) for f in context().__dataclass_fields__)


@pytest.mark.parametrize("flag", list(ExplicitSupportContext.__dataclass_fields__))
def test_all_context_facts_required(flag):
    f, s = pair()
    c = replace(context(), **{flag: False})
    with pytest.raises(ValueError, match=flag):
        validate_explicit_spear_support(f, s, c)


def test_missing_context_rejected():
    with pytest.raises(ValueError):
        validate_explicit_spear_support(*pair(), None)


def test_non_spear_is_not_supported():
    f, s = pair()
    s.effective_wargear = [S(id="WG_HAND_WEAPON")]
    with pytest.raises(ValueError, match="spear"):
        validate_explicit_spear_support(f, s, context())


def test_war_spear_alone_remains_unverified():
    f, s = pair()
    s.effective_wargear = [S(id="WG_WAR_SPEAR")]
    with pytest.raises(ValueError):
        validate_explicit_spear_support(f, s, context())


def test_cavalry_cannot_use_standard_infantry_spear_support():
    f, s = pair()
    s.effective_model_types = {"CAVALRY"}
    with pytest.raises(ValueError, match="Infantry"):
        validate_explicit_spear_support(f, s, context())


def test_supporter_base_too_large_rejected():
    f, s = pair()
    s.effective_base_size_mm = 40
    with pytest.raises(ValueError, match="base"):
        validate_explicit_spear_support(f, s, context())


def test_same_object_cannot_self_support():
    f, _ = pair()
    f.effective_wargear = [S(id="WG_SPEAR")]
    with pytest.raises(ValueError):
        validate_explicit_spear_support(f, f, context())


def test_configured_fight_mismatch_fails_closed():
    f, s = pair()
    s.effective_fight = 5
    with pytest.raises(ValueError, match="adapter"):
        validate_explicit_spear_support(f, s, context())


@pytest.fixture
def fake_combat_engine(monkeypatch):
    benchmark = types.ModuleType("combat_benchmark")
    benchmark.DEFAULT_COMBAT_BENCHMARK = S(fight=4, attacks=1, strength=4,
                                          defence=6, wounds=1)
    monkeypatch.setitem(sys.modules, "combat_benchmark", benchmark)

    profilemod = types.ModuleType("profiles")
    def profile(**kwargs):
        return S(**kwargs)
    profilemod.Profile = profile
    monkeypatch.setitem(sys.modules, "profiles", profilemod)

    participantmod = types.ModuleType("combat_participant")
    class CombatParticipant:
        def __init__(self, *, profile, duel_dice, contributes_fight=True, can_make_strikes=True):
            self.profile=profile
            self.duel_dice=duel_dice
            self.contributes_fight=contributes_fight
            self.can_make_strikes=can_make_strikes
    participantmod.CombatParticipant = CombatParticipant
    monkeypatch.setitem(sys.modules, "combat_participant", participantmod)

    sidemod = types.ModuleType("combat_side")
    class CombatSide:
        def __init__(self, *, participants):
            self.participants=participants
        @property
        def total_duel_dice(self):
            return sum(p.duel_dice for p in self.participants)
        @property
        def highest_fight(self):
            return max(p.profile.fight for p in self.participants if p.contributes_fight)
    sidemod.CombatSide = CombatSide
    monkeypatch.setitem(sys.modules, "combat_side", sidemod)

    duelmod = types.ModuleType("duel_probability")
    def duel(first, second):
        return S(attacker_win_probability=0.625)
    duelmod.calculate_combat_side_duel_probability = duel
    monkeypatch.setitem(sys.modules, "duel_probability", duelmod)


def test_duel_uses_existing_multi_model_engine(fake_combat_engine):
    f, s = pair()
    r = calculate_explicit_support_duel(
        f, s, fighter_id="f:1", supporter_id="s:1", context=context(),
    )
    assert r["combined_duel_win_probability"] == 0.625
    assert r["combat_side_duel_dice"] == 2
    assert r["supporter_strikes_if_win"] == 1


def test_joint_support_not_sum_independent_scores(fake_combat_engine):
    f, s = pair()
    r = calculate_explicit_support_duel(
        f, s, fighter_id="f", supporter_id="s", context=context(),
    )
    assert r["supporter_not_independent_combat"] is True
    assert r["model_allocation"]["independent_model_scores_added"] is False
    assert r["candidate_raw_density"] is None


def test_no_wound_or_kill_probability_invented(fake_combat_engine):
    f, s = pair()
    r = calculate_explicit_support_duel(
        f, s, fighter_id="f", supporter_id="s", context=context(),
    )
    assert r["combined_kill_probability"] is None
    assert r["supporter_wound_evidence"] == "not_evaluated"


def test_no_production_or_calibration_changes(fake_combat_engine):
    f, s = pair()
    r = calculate_explicit_support_duel(
        f, s, fighter_id="f", supporter_id="s", context=context(),
    )
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False


def test_duplicate_identity_rejected(fake_combat_engine):
    with pytest.raises(ValueError):
        calculate_explicit_support_duel(
            *pair(), fighter_id="same", supporter_id="same", context=context(),
        )


def test_fighter_more_than_one_attack_preserved(fake_combat_engine):
    f, s = pair()
    f.effective_attacks = 2
    r = calculate_explicit_support_duel(
        f, s, fighter_id="front", supporter_id="back", context=context(),
    )
    assert r["combat_side_duel_dice"] == 3
    assert r["fighter_strikes_if_win"] == 2


def test_cannot_use_unsupported_noninteger_fighter_attacks(fake_combat_engine):
    f, s = pair()
    f.effective_attacks = .5
    with pytest.raises(ValueError):
        calculate_explicit_support_duel(
            f, s, fighter_id="front", supporter_id="back", context=context(),
        )


def test_benchmark_is_not_manipulated(fake_combat_engine):
    f, s = pair()
    r = calculate_explicit_support_duel(
        f, s, fighter_id="front", supporter_id="back", context=context(),
        benchmark=S(fight=5, attacks=1, strength=3, defence=7, wounds=1),
    )
    assert r["target"] == "ordinary_single_wound_benchmark"
    assert r["combined_kill_probability"] is None
