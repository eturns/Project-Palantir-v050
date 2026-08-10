import pytest

from hero_resource_spending import (
    spend_fate,
    spend_might,
    spend_will,
)
from hero_resource_state import HeroResourceState


def test_spend_might_returns_new_state():
    state = HeroResourceState(
        remaining_might=3,
        remaining_will=2,
        remaining_fate=1,
    )

    result = spend_might(
        state,
        amount=2,
    )

    assert result == HeroResourceState(
        remaining_might=1,
        remaining_will=2,
        remaining_fate=1,
    )

    assert state.remaining_might == 3


def test_spend_will_returns_new_state():
    state = HeroResourceState(
        remaining_might=3,
        remaining_will=2,
        remaining_fate=1,
    )

    assert spend_will(
        state,
        amount=1,
    ) == HeroResourceState(
        remaining_might=3,
        remaining_will=1,
        remaining_fate=1,
    )


def test_spend_fate_returns_new_state():
    state = HeroResourceState(
        remaining_might=3,
        remaining_will=2,
        remaining_fate=1,
    )

    assert spend_fate(
        state,
        amount=1,
    ) == HeroResourceState(
        remaining_might=3,
        remaining_will=2,
        remaining_fate=0,
    )


@pytest.mark.parametrize(
    (
        "spend_function",
        "state",
        "expected_message",
    ),
    (
        (
            spend_might,
            HeroResourceState(
                remaining_might=1,
            ),
            "Cannot spend more Might than remains.",
        ),
        (
            spend_will,
            HeroResourceState(
                remaining_will=1,
            ),
            "Cannot spend more Will than remains.",
        ),
        (
            spend_fate,
            HeroResourceState(
                remaining_fate=1,
            ),
            "Cannot spend more Fate than remains.",
        ),
    ),
)
def test_resource_spending_rejects_overspend(
    spend_function,
    state,
    expected_message,
):
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        spend_function(
            state,
            amount=2,
        )