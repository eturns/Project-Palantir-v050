"""Focused integration-contract tests for DEV-077S-I2-G2-A1."""
from types import SimpleNamespace
from fractions import Fraction
import pytest
import hero_hunting_melee as target


def profile(attacks=1, fight=3):
    return SimpleNamespace(
        effective_attacks=attacks,
        effective_fight=fight,
        effective_special_rules=(),
        effective_wargear=(),
    )


def test_requires_explicit_supported_context():
    with pytest.raises(ValueError, match="Explicit"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1)


def test_rejects_invalid_resource_state():
    with pytest.raises(ValueError, match="resource"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=0,
            ordinary_one_on_one=True)


def test_zero_wound_chance_cannot_eliminate(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability", lambda **k: SimpleNamespace(attacker_win_probability=0.5))
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(0))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(2), defender=profile(), remaining_wounds=1,
        ordinary_one_on_one=True)
    assert result.expected_wounds == 0
    assert result.elimination_probability == 0


def test_certain_wound_one_wound_no_fate(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability", lambda **k: SimpleNamespace(attacker_win_probability=0.75))
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(), defender=profile(), remaining_wounds=1,
        ordinary_one_on_one=True)
    assert result.expected_wounds == pytest.approx(0.75)
    assert result.elimination_probability == pytest.approx(0.75)


def test_more_wounds_than_attacks_cannot_eliminate(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability", lambda **k: SimpleNamespace(attacker_win_probability=1.0))
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(2), defender=profile(), remaining_wounds=3,
        ordinary_one_on_one=True)
    assert result.elimination_probability == 0

from duel_might import DuelMightStrategy


def test_strike_requires_explicit_permission():
    with pytest.raises(ValueError, match="permission"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True, attacker_might=1,
            attacker_heroic_strike=True)


def test_strike_consumes_one_might_before_duel_allocation():
    with pytest.raises(ValueError, match="exceeds"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True, attacker_might=1,
            attacker_heroic_strike=True, attacker_strike_permitted=True,
            attacker_duel_might_budget=1,
            attacker_duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)


def test_defender_might_cannot_be_reused_for_fate():
    with pytest.raises(ValueError, match="exceeds"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True, defender_might=1,
            defender_duel_might_budget=1, defender_fate_might=1,
            defender_duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)


def test_heroic_strike_changes_duel_probability(monkeypatch):
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    base = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(fight=3), defender=profile(fight=5),
        remaining_wounds=1, ordinary_one_on_one=True)
    struck = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(fight=3), defender=profile(fight=5),
        remaining_wounds=1, ordinary_one_on_one=True,
        attacker_might=1, attacker_heroic_strike=True,
        attacker_strike_permitted=True)
    assert struck.duel_win_probability > base.duel_win_probability
    assert struck.elimination_probability > base.elimination_probability
    assert struck.evidence_status == "limited_context_resource_reserved"


def test_duel_might_changes_probability(monkeypatch):
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    base = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(), defender=profile(), remaining_wounds=1,
        ordinary_one_on_one=True)
    improved = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(), defender=profile(), remaining_wounds=1,
        ordinary_one_on_one=True, attacker_might=1,
        attacker_duel_might_budget=1,
        attacker_duel_might_strategy=DuelMightStrategy.MINIMUM_TO_WIN)
    assert improved.duel_win_probability > base.duel_win_probability


def test_no_might_strategy_without_allocation():
    with pytest.raises(ValueError, match="requires an allocation"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True,
            attacker_duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL)


def _with_rules(*ids):
    return SimpleNamespace(
        effective_attacks=1, effective_fight=3,
        effective_special_rules=tuple(SimpleNamespace(rule=SimpleNamespace(id=rid)) for rid in ids),
    )


@pytest.mark.parametrize("rule", ["BRINGER_OF_DEATH"])
def test_unsupported_damage_rule_fails_closed(rule):
    with pytest.raises(ValueError, match="Incomplete Hero Hunting"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=_with_rules(rule), defender=profile(),
            remaining_wounds=1, ordinary_one_on_one=True)


def test_defender_remaining_will_requires_resource_evidence():
    with pytest.raises(ValueError, match="defensive Will"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            defender_remaining_will=1, ordinary_one_on_one=True)


def test_morgul_blade_wargear_fails_closed():
    attacker = profile()
    attacker.effective_wargear = [SimpleNamespace(id="MORGUL_BLADE")]
    with pytest.raises(ValueError, match="Morgul Blade"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=attacker, defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True)

# G2-B2 conditional special rule / weapon selection integration.
from melee_weapon_selection import MeleeWeaponSelection
from wound_context import WoundContext
from wound_attack_type import WoundAttackType
from special_rule_wound_effect import get_contextual_special_rule_wound_reroll


def _b2_profile(rules=(), keywords=(), wargear=()):
    return SimpleNamespace(
        effective_attacks=1, effective_fight=3,
        effective_special_rules=tuple(
            SimpleNamespace(rule=SimpleNamespace(id=rid), parameter=param)
            for rid, param in rules
        ),
        effective_keywords=set(keywords), effective_wargear=tuple(wargear),
    )


@pytest.mark.parametrize("rules,keywords,failed,ones", [
    ((("ANCIENT_ENEMIES", "DWARF"),), ("DWARF", "HERO"), False, True),
    ((("ANCIENT_ENEMIES", "DWARF"),), ("ELF", "HERO"), False, False),
    ((("SLAYER_OF_MEN", None),), ("HERO",), True, False),
    ((("SLAYER_OF_MEN", None),), ("WARRIOR",), False, False),
    ((("VENOM", None),), ("HERO",), True, False),
])
def test_conditional_rerolls_reach_melee_evidence(monkeypatch, rules, keywords, failed, ones):
    attacker, defender = _b2_profile(rules=rules), _b2_profile(keywords=keywords)
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **k: SimpleNamespace(attacker_win_probability=1.0))
    observed = []

    def canonical(a, d, **kwargs):
        effect = get_contextual_special_rule_wound_reroll(a, defender=d,
                                                           context=kwargs.get("context"))
        observed.append(effect)
        base = Fraction(1, 3)
        if effect.reroll_failed:
            return base + (1-base)*base
        if effect.reroll_natural_ones:
            return base + Fraction(1, 6)*base
        return base

    monkeypatch.setattr(target, "calculate_configured_wound_probability", canonical)
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=attacker, defender=defender, remaining_wounds=1,
        ordinary_one_on_one=True,
    )
    assert len(observed) == 1
    assert observed[0].reroll_failed is failed
    assert observed[0].reroll_natural_ones is ones
    assert result.expected_wounds == pytest.approx(result.elimination_probability)


def test_poisoned_weapon_selection_is_forwarded(monkeypatch):
    poisoned = SimpleNamespace(id="TEST_POISONED_SWORD",
                              special_rules=(SimpleNamespace(id="POISONED_ATTACKS"),))
    attacker = _b2_profile(wargear=(poisoned,))
    defender = _b2_profile(keywords=("HERO",))
    selection = MeleeWeaponSelection(wargear_id=poisoned.id)
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **k: SimpleNamespace(attacker_win_probability=1.0))
    effects = []

    def canonical(a, d, **kwargs):
        effects.append(get_contextual_special_rule_wound_reroll(
            a, defender=d, selection=kwargs.get("attacker_selection"),
            context=kwargs.get("context")))
        return Fraction(1, 2)

    monkeypatch.setattr(target, "calculate_configured_wound_probability", canonical)
    target.calculate_hero_hunting_melee_evidence(
        attacker=attacker, defender=defender, remaining_wounds=1,
        ordinary_one_on_one=True, attacker_melee_weapon=selection)
    assert effects[0].reroll_natural_ones is True


def test_unowned_weapon_rejected():
    with pytest.raises(ValueError, match="not held"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True,
            attacker_melee_weapon=MeleeWeaponSelection(wargear_id="NOT_EQUIPPED"))


@pytest.mark.parametrize("context", [
    WoundContext(defender_trapped=True),
    WoundContext(attacker_natural_duel_roll=6),
    WoundContext(attack_type=WoundAttackType.SHOOTING),
])
def test_unsupported_conditional_context_rejected(context):
    with pytest.raises(ValueError, match="Incomplete Hero Hunting"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            ordinary_one_on_one=True, wound_context=context)


# G2-B3: deterministic multi-wound damage must be resolved before Fate.
def test_mighty_blow_kills_two_wound_target_with_one_success(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **kw: SimpleNamespace(attacker_win_probability=1.0))
    monkeypatch.setattr(target, "calculate_configured_wound_probability",
                        lambda *args, **kw: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("MIGHTY_BLOW"), defender=profile(),
        remaining_wounds=2, ordinary_one_on_one=True)
    assert result.wounds_per_successful_strike == 2
    assert result.expected_wounds == pytest.approx(2.0)
    assert result.elimination_probability == pytest.approx(1.0)


def test_mighty_blow_survival_probability_uses_two_wounds_before_fate(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **kw: SimpleNamespace(attacker_win_probability=1.0))
    monkeypatch.setattr(target, "calculate_configured_wound_probability",
                        lambda *args, **kw: Fraction(1))
    defender = profile()
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("MIGHTY_BLOW"), defender=defender,
        remaining_wounds=2, remaining_fate=1, ordinary_one_on_one=True)
    assert result.elimination_probability == pytest.approx(1 / 2)


def test_mighty_blow_probability_counts_successful_strikes_not_extra_hit_rolls(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **kw: SimpleNamespace(attacker_win_probability=Fraction(1, 2)))
    monkeypatch.setattr(target, "calculate_configured_wound_probability",
                        lambda *args, **kw: Fraction(1, 2))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("MIGHTY_BLOW"), defender=profile(),
        remaining_wounds=2, ordinary_one_on_one=True)
    assert result.expected_wounds == pytest.approx(0.5)
    assert result.elimination_probability == pytest.approx(0.25)


def test_mighty_blow_cannot_eliminate_three_wound_target_with_one_hit(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **kw: SimpleNamespace(attacker_win_probability=1.0))
    monkeypatch.setattr(target, "calculate_configured_wound_probability",
                        lambda *args, **kw: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("MIGHTY_BLOW"), defender=profile(),
        remaining_wounds=3, ordinary_one_on_one=True)
    assert result.elimination_probability == 0


# B4: exact correlated natural roll / Duel win / doubled damage.
def _executioner_attacker(attacks=1, fight=4):
    model = profile(attacks=attacks, fight=fight)
    model.effective_special_rules = (
        SimpleNamespace(rule=SimpleNamespace(id="EXECUTIONER")),
    )
    return model


def test_executioner_one_die_fight_advantage_exact_joint_probability(monkeypatch):
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_executioner_attacker(), defender=profile(fight=3),
        remaining_wounds=2, ordinary_one_on_one=True,
    )
    assert result.elimination_probability == pytest.approx(1 / 6)
    assert result.wounds_per_successful_strike is None
    assert result.evidence_status == "limited_context_executioner_joint"


def test_executioner_equal_fight_roll_off_correlated(monkeypatch):
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_executioner_attacker(fight=3), defender=profile(fight=3),
        remaining_wounds=2, ordinary_one_on_one=True,
    )
    assert result.elimination_probability == pytest.approx(11 / 72)


def test_executioner_two_attack_dice_natural_six(monkeypatch):
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a: Fraction(1))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_executioner_attacker(attacks=2), defender=profile(fight=3),
        remaining_wounds=4, ordinary_one_on_one=True,
    )
    assert result.elimination_probability == pytest.approx(11 / 36)


def test_executioner_rejects_duel_might_until_resource_correlations_supported():
    with pytest.raises(ValueError, match="Executioner resource"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=_executioner_attacker(), defender=profile(),
            remaining_wounds=1, ordinary_one_on_one=True,
            attacker_might=1, attacker_duel_might_budget=1,
            attacker_duel_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
        )

# B5: one encounter, explicit Will-as-Fate, no cross-action Will reuse.
def _b5_certain_strike(monkeypatch):
    monkeypatch.setattr(target, "calculate_basic_duel_probability",
                        lambda **kw: SimpleNamespace(attacker_win_probability=1.0))
    monkeypatch.setattr(target, "calculate_configured_wound_probability",
                        lambda *args, **kw: Fraction(1))


def test_will_as_fate_reduces_elimination_probability(monkeypatch):
    _b5_certain_strike(monkeypatch)
    seen = []
    def canonical(defender, state):
        seen.append((state.remaining_fate, state.remaining_will))
        return state.remaining_fate + state.remaining_will
    monkeypatch.setattr(target, "get_available_fate_attempts", canonical)
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(), defender=profile(), remaining_wounds=1,
        defender_remaining_will=1, ordinary_one_on_one=True)
    assert seen == [(0, 1)]
    assert result.elimination_probability == pytest.approx(0.5)
    assert result.evidence_status == "limited_context_will_conversion"


def test_will_reserved_elsewhere_is_not_used_as_fate(monkeypatch):
    _b5_certain_strike(monkeypatch)
    def canonical(defender, state):
        return state.remaining_fate + state.remaining_will
    monkeypatch.setattr(target, "get_available_fate_attempts", canonical)
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(), defender=profile(), remaining_wounds=1,
        defender_remaining_will=2, defender_will_reserved_elsewhere=1,
        ordinary_one_on_one=True)
    assert result.elimination_probability == pytest.approx(0.5)
    no_will = target.calculate_hero_hunting_melee_evidence(
        attacker=profile(), defender=profile(), remaining_wounds=1,
        defender_remaining_will=2, defender_will_reserved_elsewhere=2,
        ordinary_one_on_one=True)
    assert no_will.elimination_probability == pytest.approx(1.0)


def test_rejects_invalid_will_reservation():
    with pytest.raises(ValueError, match="Will resource allocation"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            defender_remaining_will=1, defender_will_reserved_elsewhere=2,
            ordinary_one_on_one=True)


def test_rejects_unproven_will_as_fate_permission(monkeypatch):
    monkeypatch.setattr(target, "get_available_fate_attempts", lambda defender, state: state.remaining_fate)
    with pytest.raises(ValueError, match="Incomplete Hero Hunting defensive Will conversion"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=profile(), defender=profile(), remaining_wounds=1,
            defender_remaining_will=1, ordinary_one_on_one=True)


def test_will_conversion_and_mighty_blow_share_survival_engine(monkeypatch):
    _b5_certain_strike(monkeypatch)
    monkeypatch.setattr(target, "get_available_fate_attempts",
                        lambda defender, state: state.remaining_fate + state.remaining_will)
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("MIGHTY_BLOW"), defender=profile(),
        remaining_wounds=2, defender_remaining_will=1,
        ordinary_one_on_one=True)
    assert result.expected_wounds == pytest.approx(2)
    assert result.elimination_probability == pytest.approx(0.5)


# B6: Drain Soul and selected one-use Morgul Blade act after wound prevention.
from morgul_blade_state import MorgulBladeState
from melee_weapon_selection import MeleeWeaponSelection
from post_prevention_effect import PostPreventionEffect


def test_drain_soul_eliminates_multi_wound_target_after_one_unprevented_wound(monkeypatch):
    _b5_certain_strike(monkeypatch)
    attacker = _with_rules("DRAIN_SOUL")
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=attacker, defender=profile(), remaining_wounds=5,
        ordinary_one_on_one=True)
    assert result.elimination_probability == pytest.approx(1)
    assert result.expected_wounds == pytest.approx(1)
    assert result.evidence_status == "limited_context_post_prevention"


def test_drain_soul_fate_can_prevent_activation(monkeypatch):
    _b5_certain_strike(monkeypatch)
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("DRAIN_SOUL"), defender=profile(),
        remaining_wounds=5, remaining_fate=1, ordinary_one_on_one=True)
    assert result.elimination_probability == pytest.approx(0.5)


def test_drain_soul_does_not_trigger_if_no_wound(monkeypatch):
    _b5_certain_strike(monkeypatch)
    monkeypatch.setattr(target, "calculate_configured_wound_probability", lambda *a, **kw: Fraction(0))
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=_with_rules("DRAIN_SOUL"), defender=profile(),
        remaining_wounds=5, ordinary_one_on_one=True)
    assert result.elimination_probability == 0


def test_morgul_blade_selected_active_effect(monkeypatch):
    _b5_certain_strike(monkeypatch)
    blade = SimpleNamespace(id="WG_MORGUL_BLADE")
    attacker = profile()
    attacker.effective_wargear = (blade,)
    attacker.profile = SimpleNamespace(strength=3, attacks=1)
    attacker.effective_strength = 3
    selection = MeleeWeaponSelection(wargear_id="WG_MORGUL_BLADE")
    result = target.calculate_hero_hunting_melee_evidence(
        attacker=attacker, defender=profile(), remaining_wounds=4,
        attacker_melee_weapon=selection,
        morgul_blade_state=MorgulBladeState(used=True, active_this_combat=True),
        ordinary_one_on_one=True)
    assert result.elimination_probability == pytest.approx(1)


def test_morgul_blade_inactive_cannot_be_selected(monkeypatch):
    blade = SimpleNamespace(id="WG_MORGUL_BLADE")
    attacker = profile()
    attacker.effective_wargear = (blade,)
    with pytest.raises(ValueError, match="Morgul Blade activation"):
        target.calculate_hero_hunting_melee_evidence(
            attacker=attacker, defender=profile(), remaining_wounds=4,
            attacker_melee_weapon=MeleeWeaponSelection(wargear_id="WG_MORGUL_BLADE"),
            morgul_blade_state=MorgulBladeState(), ordinary_one_on_one=True)
