from torturer_state import TorturerState
from torturer_wound_effect import (
    get_torturer_wound_reroll,
)
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from wound_reroll import WoundReroll


def test_torturer_has_no_wound_reroll_at_zero_kills():
    result = get_torturer_wound_reroll(
        TorturerState(
            kills_in_combat=0,
        )
    )

    assert result == WoundReroll()


def test_torturer_rerolls_natural_ones_after_one_kill():
    result = get_torturer_wound_reroll(
        TorturerState(
            kills_in_combat=1,
        )
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )


def test_torturer_still_only_rerolls_ones_at_three_kills():
    result = get_torturer_wound_reroll(
        TorturerState(
            kills_in_combat=3,
        )
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )


def test_torturer_rerolls_all_failed_wounds_after_five_kills():
    result = get_torturer_wound_reroll(
        TorturerState(
            kills_in_combat=5,
        )
    )

    assert result == WoundReroll(
        reroll_failed=True,
        reroll_natural_ones=True,
    )


def test_torturer_does_not_apply_to_non_strike_attack():
    context = WoundContext(
        attack_type=WoundAttackType.SHOOTING,
    )

    result = get_torturer_wound_reroll(
        TorturerState(
            kills_in_combat=5,
        ),
        context=context,
    )

    assert result == WoundReroll()