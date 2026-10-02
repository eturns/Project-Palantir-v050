import pytest

from morgul_blade_state import (
    MorgulBladeState,
)
from morgul_blade_transition import (
    end_morgul_blade_combat,
    use_morgul_blade,
)


def test_morgul_blade_starts_unused_and_inactive():
    state = MorgulBladeState()

    assert state.used is False
    assert state.active_this_combat is False


def test_using_morgul_blade_marks_it_used_and_active():
    original = MorgulBladeState()

    updated = use_morgul_blade(
        original,
    )

    assert original.used is False
    assert original.active_this_combat is False

    assert updated.used is True
    assert updated.active_this_combat is True


def test_ending_combat_keeps_morgul_blade_spent_but_inactive():
    active = use_morgul_blade(
        MorgulBladeState()
    )

    ended = end_morgul_blade_combat(
        active,
    )

    assert ended.used is True
    assert ended.active_this_combat is False


def test_morgul_blade_cannot_be_used_twice():
    state = MorgulBladeState(
        used=True,
        active_this_combat=False,
    )

    with pytest.raises(
        ValueError,
        match="already been used",
    ):
        use_morgul_blade(
            state,
        )


def test_morgul_blade_cannot_be_reused_after_combat_ends():
    active = use_morgul_blade(
        MorgulBladeState()
    )

    ended = end_morgul_blade_combat(
        active,
    )

    with pytest.raises(
        ValueError,
        match="already been used",
    ):
        use_morgul_blade(
            ended,
        )