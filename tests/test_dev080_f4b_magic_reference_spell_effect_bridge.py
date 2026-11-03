"""
Project Palantír
DEV-080-F4B: Reference Spell Effect Bridge Tests.

Author: Edward Turns (Project Lead)

Verifies existing rules-backed spell calculations
without introducing arbitrary impact weights.
"""

from fractions import Fraction

import pytest

from magic_reference_spell_effect_bridge import (
    evaluate_reference_spell_effect,
)


REFERENCE_CONTEXTS = (
    ("CHILL_SOUL", {
        "target_remaining_wounds": 1,
        "conditional_wound_not_prevented_probability":
            Fraction(1),
    }),
    ("COMPEL", {
        "target_move_inches": 6,
        "target_engaged_in_combat": False,
    }),
    ("CURSE", {
        "target_remaining_fate": 2,
        "target_part": "model",
    }),
    ("DRAIN_COURAGE", {
        "target_courage_required_roll": 4,
        "target_part": "model",
    }),
    ("FOG_OF_DISARRAY", {}),
    ("INSTIL_FEAR", {}),
    ("TRANSFIX", {}),
    ("WITHER", {
        "target_current_strength": 4,
        "target_part": "model",
    }),
    ("YOUR_STAFF_IS_BROKEN", {
        "target_has_staff_of_power": True,
    }),
)


@pytest.mark.parametrize(
    "spell_id,context",
    REFERENCE_CONTEXTS,
)
def test_all_nine_verified_spells(
    spell_id,
    context,
):
    result = evaluate_reference_spell_effect(
        spell_id=spell_id,
        effect_probability=Fraction(1, 2),
        context=context,
    )

    assert result.spell_id == spell_id
    assert result.effect_probability == Fraction(1, 2)
    assert result.mechanical_evidence.spell_id == spell_id
    assert result.dashboard_score is None
    assert result.scenario_score is None


def test_chill_soul_preserves_elimination_probability():
    result = evaluate_reference_spell_effect(
        spell_id="CHILL_SOUL",
        effect_probability=Fraction(1, 2),
        context={
            "target_remaining_wounds": 1,
            "conditional_wound_not_prevented_probability":
                Fraction(1),
        },
    )

    assert (
        result.mechanical_evidence.target_elimination_probability
        == Fraction(1, 2)
    )


def test_transfix_preserves_control_restrictions():
    result = evaluate_reference_spell_effect(
        spell_id="TRANSFIX",
        effect_probability=Fraction(1, 2),
        context={},
    )

    assert result.mechanical_evidence.activation_blocked
    assert result.mechanical_evidence.heroic_actions_blocked
    assert result.mechanical_evidence.shooting_blocked


def test_wither_preserves_strength_reduction():
    result = evaluate_reference_spell_effect(
        spell_id="WITHER",
        effect_probability=Fraction(1, 2),
        context={
            "target_current_strength": 4,
            "target_part": "model",
        },
    )

    assert result.mechanical_evidence.resulting_strength == 3


def test_foil_magic_remains_unverified():
    with pytest.raises(ValueError, match="No verified effect"):
        evaluate_reference_spell_effect(
            spell_id="FOIL_MAGIC",
            effect_probability=Fraction(1, 2),
            context={},
        )


def test_missing_context_rejected():
    with pytest.raises(
        ValueError,
        match="Missing reference context",
    ):
        evaluate_reference_spell_effect(
            spell_id="WITHER",
            effect_probability=Fraction(1, 2),
            context={},
        )


def test_invalid_probability_rejected():
    with pytest.raises(ValueError):
        evaluate_reference_spell_effect(
            spell_id="TRANSFIX",
            effect_probability=Fraction(3, 2),
            context={},
        )