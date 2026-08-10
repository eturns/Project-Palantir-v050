import pytest

from hero_resource_state import HeroResourceState


def test_hero_resource_state_stores_remaining_resources():
    state = HeroResourceState(
        remaining_might=3,
        remaining_will=2,
        remaining_fate=1,
    )

    assert state.remaining_might == 3
    assert state.remaining_will == 2
    assert state.remaining_fate == 1


def test_hero_resource_state_defaults_to_zero():
    assert HeroResourceState() == HeroResourceState(
        remaining_might=0,
        remaining_will=0,
        remaining_fate=0,
    )


@pytest.mark.parametrize(
    ("field_name", "expected_message"),
    (
        (
            "remaining_might",
            "Remaining Might cannot be negative.",
        ),
        (
            "remaining_will",
            "Remaining Will cannot be negative.",
        ),
        (
            "remaining_fate",
            "Remaining Fate cannot be negative.",
        ),
    ),
)
def test_hero_resource_state_rejects_negative_resources(
    field_name,
    expected_message,
):
    values = {
        "remaining_might": 0,
        "remaining_will": 0,
        "remaining_fate": 0,
    }
    values[field_name] = -1

    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        HeroResourceState(**values)