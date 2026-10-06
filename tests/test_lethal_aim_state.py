import pytest

from lethal_aim_state import (
    LethalAimSpend,
    LethalAimState,
    expire_lethal_aim_at_end_of_turn,
    refresh_lethal_aim_for_new_turn,
    spend_lethal_aim_might,
)


@pytest.mark.parametrize(
    "spend",
    (
        LethalAimSpend.TO_HIT,
        LethalAimSpend.TO_WOUND,
        LethalAimSpend.IN_THE_WAY,
    ),
)
def test_lethal_aim_allows_its_three_legal_shooting_spends(
    spend,
):
    state = LethalAimState()

    assert state.can_spend_on(
        spend
    ) is True


def test_spending_lethal_aim_consumes_the_free_point():
    state = spend_lethal_aim_might(
        LethalAimState(),
        LethalAimSpend.TO_HIT,
    )

    assert state.free_might_available is False


def test_lethal_aim_cannot_be_spent_twice_in_same_turn():
    state = spend_lethal_aim_might(
        LethalAimState(),
        LethalAimSpend.TO_WOUND,
    )

    with pytest.raises(
        ValueError,
        match="Lethal Aim free Might is not available",
    ):
        spend_lethal_aim_might(
            state,
            LethalAimSpend.IN_THE_WAY,
        )


def test_unused_lethal_aim_expires_at_end_of_turn():
    state = expire_lethal_aim_at_end_of_turn(
        LethalAimState()
    )

    assert state.free_might_available is False


def test_lethal_aim_refreshes_for_new_turn():
    spent_state = LethalAimState(
        free_might_available=False,
    )

    refreshed = refresh_lethal_aim_for_new_turn()

    assert refreshed.free_might_available is True