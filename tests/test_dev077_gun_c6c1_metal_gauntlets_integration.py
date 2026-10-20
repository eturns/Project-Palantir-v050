"""Check Metal Gauntlets integration inside the real configured wound pipeline."""
from types import SimpleNamespace as NS
from fractions import Fraction
import pytest
import configured_wound_probability as cwp
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def combatant(*, name='Gundabad Catapult Troll', gear='Metal Gauntlets'):
    return NS(profile=NS(name=name), effective_wargear=(NS(name=gear),),
              effective_strength=8, effective_special_rules=())


@pytest.fixture
def pipeline(monkeypatch):
    strengths = []
    monkeypatch.setattr(cwp, 'get_morgul_blade_combat_strength', lambda *a, **k: 8)
    monkeypatch.setattr(cwp, 'get_effective_defence', lambda *a, **k: 8)
    monkeypatch.setattr(cwp, 'get_wound_target', lambda *, strength, defence:
                        strengths.append(strength) or (strength, defence))
    monkeypatch.setattr(cwp, 'uses_i_am_the_master', lambda *a: False)
    monkeypatch.setattr(cwp, 'get_wargear_mechanical_effect_definitions', lambda *a, **k: ())
    monkeypatch.setattr(cwp, 'get_special_rule_mechanical_effect_definitions', lambda *a: ())
    monkeypatch.setattr(cwp, 'resolved_wound_modifier', lambda *a: None)
    monkeypatch.setattr(cwp, 'get_lethal_aim_wound_modifier', lambda *a, **k: None)
    monkeypatch.setattr(cwp, 'get_special_rule_wound_modifiers', lambda *a, **k: ())
    monkeypatch.setattr(cwp, 'combine_wound_modifiers', lambda *a: None)
    monkeypatch.setattr(cwp, 'resolved_wound_reroll', lambda *a: None)
    monkeypatch.setattr(cwp, 'get_contextual_special_rule_wound_reroll',
                        lambda *a, **k: NS(reroll_failed=False, reroll_natural_ones=False))
    monkeypatch.setattr(cwp, 'get_modified_wound_probability_with_reroll',
                        lambda *, target, modifier, reroll: Fraction(target[0], 10))
    return strengths


def test_normal_strike_uses_strength_ten(pipeline):
    assert cwp.calculate_configured_wound_probability(combatant(), combatant()) == 1
    assert pipeline == [10]


def test_explicit_melee_strike_uses_strength_ten(pipeline):
    cwp.calculate_configured_wound_probability(
        combatant(), combatant(), context=WoundContext(attack_type=WoundAttackType.STRIKE))
    assert pipeline == [10]


def test_shooting_context_preserves_original_strength(pipeline):
    cwp.calculate_configured_wound_probability(
        combatant(), combatant(), context=WoundContext(attack_type=WoundAttackType.SHOOTING))
    assert pipeline == [8]


def test_other_monster_does_not_gain_bonus(pipeline):
    cwp.calculate_configured_wound_probability(combatant(name='Troll Brute'), combatant())
    assert pipeline == [8]


def test_missing_gauntlets_does_not_gain_bonus(pipeline):
    cwp.calculate_configured_wound_probability(combatant(gear='Hand weapon'), combatant())
    assert pipeline == [8]


def test_underlying_strength_unchanged(pipeline):
    attacker = combatant()
    cwp.calculate_configured_wound_probability(attacker, combatant())
    assert attacker.effective_strength == 8
