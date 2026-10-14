from fractions import Fraction
import pytest
from hero_hunting_spell_outcomes import (
    SpellOutcomeKind, VerifiedSpellOutcome, calculate_declared_spell_hero_hunting,
)


def _declared(kind, **kwargs):
    return VerifiedSpellOutcome(
        spell_id="TEST_SPELL", kind=kind,
        rule_source="independently verified hypothetical test rule", **kwargs
    )


def test_unknown_spell_effect_fails_closed():
    with pytest.raises(ValueError, match="not mechanically verified"):
        calculate_declared_spell_hero_hunting(
            outcome=None, effect_probability=Fraction(1, 2), remaining_wounds=1
        )


def test_hero_control_is_not_called_an_elimination():
    result = calculate_declared_spell_hero_hunting(
        outcome=_declared(SpellOutcomeKind.HERO_CONTROL, controls_target=True),
        effect_probability=Fraction(1, 3), remaining_wounds=1,
    )
    assert result.conditional_hero_control_probability == Fraction(1, 3)
    assert result.direct_elimination_probability is None


def test_direct_wound_without_defence_verification_fails_closed():
    with pytest.raises(ValueError, match="defensive/prevention"):
        calculate_declared_spell_hero_hunting(
            outcome=_declared(SpellOutcomeKind.DIRECT_WOUNDS, wounds_on_effect=1),
            effect_probability=Fraction(1, 2), remaining_wounds=1,
        )


def test_explicit_damage_below_remaining_wounds_not_elimination():
    result = calculate_declared_spell_hero_hunting(
        outcome=_declared(SpellOutcomeKind.DIRECT_WOUNDS, wounds_on_effect=1),
        effect_probability=Fraction(2, 5), remaining_wounds=2,
        defensive_prevention_resolved=True,
    )
    assert result.direct_elimination_probability == 0
    assert result.conditional_wounds == 1


def test_explicit_lethal_damage_matches_effect_probability():
    result = calculate_declared_spell_hero_hunting(
        outcome=_declared(SpellOutcomeKind.DIRECT_WOUNDS, wounds_on_effect=2),
        effect_probability=Fraction(2, 5), remaining_wounds=2,
        defensive_prevention_resolved=True,
    )
    assert result.direct_elimination_probability == Fraction(2, 5)


def test_explicit_removal_requires_defence_verification():
    with pytest.raises(ValueError, match="defensive/prevention"):
        calculate_declared_spell_hero_hunting(
            outcome=_declared(SpellOutcomeKind.REMOVE_TARGET),
            effect_probability=Fraction(1, 2), remaining_wounds=4,
        )


@pytest.mark.parametrize("kind,kw", [
    (SpellOutcomeKind.DIRECT_WOUNDS, {}),
    (SpellOutcomeKind.DIRECT_WOUNDS, {"wounds_on_effect": 0}),
    (SpellOutcomeKind.HERO_CONTROL, {}),
    (SpellOutcomeKind.HERO_CONTROL, {"controls_target": False}),
    (SpellOutcomeKind.REMOVE_TARGET, {"wounds_on_effect": 2}),
])
def test_invalid_effect_declarations_rejected(kind, kw):
    with pytest.raises(ValueError):
        _declared(kind, **kw)
