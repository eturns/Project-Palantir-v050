from duel_modifier import (
    DuelModifier,
    apply_duel_modifier,
    apply_duel_modifier_to_rolls,
)

def test_duel_modifier_defaults_to_zero():
    modifier = DuelModifier()

    assert modifier.value == 0
    assert modifier.ignored_on_natural_six is False


def test_duel_modifier_stores_penalty():
    modifier = DuelModifier(
        value=-1,
    )

    assert modifier.value == -1


def test_duel_modifier_can_be_ignored_on_natural_six():
    modifier = DuelModifier(
        value=-1,
        ignored_on_natural_six=True,
    )

    assert modifier.value == -1
    assert modifier.ignored_on_natural_six is True

def test_duel_penalty_reduces_roll():
    modifier = DuelModifier(
        value=-1,
    )

    assert apply_duel_modifier(
        natural_roll=4,
        modifier=modifier,
    ) == 3


def test_duel_roll_cannot_be_modified_below_one():
    modifier = DuelModifier(
        value=-1,
    )

    assert apply_duel_modifier(
        natural_roll=1,
        modifier=modifier,
    ) == 1


def test_two_handed_penalty_is_ignored_on_natural_six():
    modifier = DuelModifier(
        value=-1,
        ignored_on_natural_six=True,
    )

    assert apply_duel_modifier(
        natural_roll=6,
        modifier=modifier,
    ) == 6

def test_duel_modifier_applies_to_all_rolls():
    modifier = DuelModifier(
        value=-1,
    )

    assert apply_duel_modifier_to_rolls(
        rolls=(2, 4, 5),
        modifier=modifier,
    ) == (1, 3, 4)


def test_natural_six_exception_applies_per_die():
    modifier = DuelModifier(
        value=-1,
        ignored_on_natural_six=True,
    )

    assert apply_duel_modifier_to_rolls(
        rolls=(4, 6),
        modifier=modifier,
    ) == (3, 6)