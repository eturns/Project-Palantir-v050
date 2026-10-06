from price_of_failure_state import (
    PriceOfFailureState,
)


def test_price_of_failure_requires_declaration():
    state = PriceOfFailureState(
        declared=False,
        within_azog_range=True,
    )

    assert state.can_use is False


def test_price_of_failure_requires_azog_within_three_inches():
    state = PriceOfFailureState(
        declared=True,
        within_azog_range=False,
    )

    assert state.can_use is False


def test_price_of_failure_can_be_used_when_declared_and_in_range():
    state = PriceOfFailureState(
        declared=True,
        within_azog_range=True,
    )

    assert state.can_use is True