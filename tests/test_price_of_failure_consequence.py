from defensive_state import DefensiveState
from price_of_failure_consequence import (
    apply_price_of_failure_loss,
)
from price_of_failure_state import (
    PriceOfFailureState,
)


def test_price_of_failure_causes_one_wound_after_lost_duel():
    result = apply_price_of_failure_loss(
        DefensiveState(
            remaining_wounds=2,
            remaining_fate=1,
        ),
        PriceOfFailureState(
            declared=True,
            within_azog_range=True,
        ),
        lost_duel=True,
    )

    assert result.remaining_wounds == 1
    assert result.remaining_fate == 1


def test_price_of_failure_does_not_wound_after_winning_duel():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
    )

    result = apply_price_of_failure_loss(
        state,
        PriceOfFailureState(
            declared=True,
            within_azog_range=True,
        ),
        lost_duel=False,
    )

    assert result == state


def test_price_of_failure_does_not_wound_when_not_declared():
    state = DefensiveState(
        remaining_wounds=2,
    )

    result = apply_price_of_failure_loss(
        state,
        PriceOfFailureState(
            declared=False,
            within_azog_range=True,
        ),
        lost_duel=True,
    )

    assert result == state


def test_price_of_failure_does_not_wound_when_out_of_range():
    state = DefensiveState(
        remaining_wounds=2,
    )

    result = apply_price_of_failure_loss(
        state,
        PriceOfFailureState(
            declared=True,
            within_azog_range=False,
        ),
        lost_duel=True,
    )

    assert result == state


def test_price_of_failure_cannot_reduce_wounds_below_zero():
    result = apply_price_of_failure_loss(
        DefensiveState(
            remaining_wounds=0,
        ),
        PriceOfFailureState(
            declared=True,
            within_azog_range=True,
        ),
        lost_duel=True,
    )

    assert result.remaining_wounds == 0