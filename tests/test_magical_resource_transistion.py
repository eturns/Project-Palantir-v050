import pytest

from hero_resource_state import HeroResourceState
from magical_resource_transition import (
    MagicalResourceSpend,
    apply_magical_resource_spend,
)


def test_magical_resource_spend_reduces_will_and_might():
    state = HeroResourceState(
        remaining_might=2,
        remaining_will=3,
        remaining_fate=1,
    )

    result = apply_magical_resource_spend(
        state,
        MagicalResourceSpend(
            will=2,
            might=1,
        ),
    )

    assert result == HeroResourceState(
        remaining_might=1,
        remaining_will=1,
        remaining_fate=1,
    )


def test_magical_resource_spend_is_immutable():
    state = HeroResourceState(
        remaining_might=2,
        remaining_will=3,
    )

    apply_magical_resource_spend(
        state,
        MagicalResourceSpend(
            will=1,
            might=1,
        ),
    )

    assert state == HeroResourceState(
        remaining_might=2,
        remaining_will=3,
    )


def test_magical_resource_spend_rejects_will_overspend():
    with pytest.raises(ValueError):
        apply_magical_resource_spend(
            HeroResourceState(
                remaining_will=1,
            ),
            MagicalResourceSpend(
                will=2,
            ),
        )


def test_magical_resource_spend_rejects_might_overspend():
    with pytest.raises(ValueError):
        apply_magical_resource_spend(
            HeroResourceState(
                remaining_might=1,
            ),
            MagicalResourceSpend(
                might=2,
            ),
        )