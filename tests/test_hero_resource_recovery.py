import pytest

from hero_resource_recovery import regain_will
from hero_resource_state import HeroResourceState


def test_regain_will_returns_new_state():
    state = HeroResourceState(
        remaining_might=2,
        remaining_will=1,
        remaining_fate=1,
    )

    result = regain_will(
        state,
        amount=1,
        starting_will=3,
    )

    assert result == HeroResourceState(
        remaining_might=2,
        remaining_will=2,
        remaining_fate=1,
    )

    assert state.remaining_will == 1


def test_regain_will_cannot_exceed_starting_value():
    state = HeroResourceState(
        remaining_will=2,
    )

    assert regain_will(
        state,
        amount=5,
        starting_will=3,
    ).remaining_will == 3


def test_regain_will_rejects_negative_amount():
    with pytest.raises(
        ValueError,
        match="Will recovery amount cannot be negative.",
    ):
        regain_will(
            HeroResourceState(),
            amount=-1,
            starting_will=3,
        )


def test_regain_will_rejects_negative_starting_value():
    with pytest.raises(
        ValueError,
        match="Starting Will cannot be negative.",
    ):
        regain_will(
            HeroResourceState(),
            amount=1,
            starting_will=-1,
        )