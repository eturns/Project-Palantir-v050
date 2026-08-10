import pytest

from wound_target import WoundTarget


def test_wound_target_accepts_single_roll():
    target = WoundTarget(
        first_roll=4,
    )

    assert target.first_roll == 4
    assert target.second_roll is None


def test_wound_target_accepts_two_stage_roll():
    target = WoundTarget(
        first_roll=6,
        second_roll=4,
    )

    assert target.first_roll == 6
    assert target.second_roll == 4


@pytest.mark.parametrize(
    "first_roll",
    [
        2,
        7,
    ],
)
def test_wound_target_rejects_invalid_first_roll(
    first_roll: int,
):
    with pytest.raises(
        ValueError,
        match="first_roll must be between 3 and 6",
    ):
        WoundTarget(
            first_roll=first_roll,
        )


def test_wound_target_rejects_second_roll_without_six():
    with pytest.raises(
        ValueError,
        match="second_roll requires first_roll to be 6",
    ):
        WoundTarget(
            first_roll=5,
            second_roll=4,
        )


@pytest.mark.parametrize(
    "second_roll",
    [
        3,
        7,
    ],
)
def test_wound_target_rejects_invalid_second_roll(
    second_roll: int,
):
    with pytest.raises(
        ValueError,
        match="second_roll must be between 4 and 6",
    ):
        WoundTarget(
            first_roll=6,
            second_roll=second_roll,
        )


def test_wound_target_is_immutable():
    target = WoundTarget(
        first_roll=4,
    )

    with pytest.raises(
        AttributeError,
    ):
        target.first_roll = 5