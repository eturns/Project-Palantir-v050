from wound_modifier import (
    WoundModifier,
    combine_wound_modifiers,
)

def test_wound_modifier_defaults_to_zero():
    modifier = WoundModifier()

    assert modifier.to_wound == 0


def test_wound_modifier_stores_positive_modifier():
    modifier = WoundModifier(
        to_wound=1,
    )

    assert modifier.to_wound == 1


def test_wound_modifier_stores_negative_modifier():
    modifier = WoundModifier(
        to_wound=-1,
    )

    assert modifier.to_wound == -1

def test_combine_no_wound_modifiers():
    modifier = combine_wound_modifiers(())

    assert modifier == WoundModifier()


def test_combine_positive_wound_modifiers():
    modifier = combine_wound_modifiers(
        (
            WoundModifier(to_wound=1),
            WoundModifier(to_wound=1),
        )
    )

    assert modifier == WoundModifier(
        to_wound=2,
    )


def test_combine_positive_and_negative_wound_modifiers():
    modifier = combine_wound_modifiers(
        (
            WoundModifier(to_wound=1),
            WoundModifier(to_wound=-1),
        )
    )

    assert modifier == WoundModifier(
        to_wound=0,
    )