import pytest

from master_of_the_nazgul import (
    get_master_of_the_nazgul_range,
    get_master_of_the_nazgul_resurrection_modifier,
    is_within_master_of_the_nazgul_range,
)


def test_twenty_or_more_will_gives_eighteen_inch_range():
    assert get_master_of_the_nazgul_range(20) == 18
    assert get_master_of_the_nazgul_range(25) == 18


def test_ten_to_nineteen_will_gives_twelve_inch_range():
    assert get_master_of_the_nazgul_range(10) == 12
    assert get_master_of_the_nazgul_range(19) == 12


def test_nine_or_fewer_will_gives_six_inch_range():
    assert get_master_of_the_nazgul_range(0) == 6
    assert get_master_of_the_nazgul_range(9) == 6


def test_master_of_the_nazgul_range_rejects_negative_will():
    with pytest.raises(
        ValueError,
        match="Remaining Will cannot be negative.",
    ):
        get_master_of_the_nazgul_range(-1)

def test_nazgul_inside_active_range_is_eligible():
    assert is_within_master_of_the_nazgul_range(
        remaining_will=20,
        distance_inches=18,
    )


def test_nazgul_outside_active_range_is_not_eligible():
    assert not is_within_master_of_the_nazgul_range(
        remaining_will=20,
        distance_inches=18.1,
    )


def test_range_changes_with_remaining_will():
    assert is_within_master_of_the_nazgul_range(
        remaining_will=10,
        distance_inches=12,
    )

    assert not is_within_master_of_the_nazgul_range(
        remaining_will=10,
        distance_inches=12.1,
    )


def test_six_inch_band_applies_at_low_will():
    assert is_within_master_of_the_nazgul_range(
        remaining_will=9,
        distance_inches=6,
    )

    assert not is_within_master_of_the_nazgul_range(
        remaining_will=9,
        distance_inches=6.1,
    )


def test_master_of_the_nazgul_range_rejects_negative_distance():
    with pytest.raises(
        ValueError,
        match="Distance cannot be negative.",
    ):
        is_within_master_of_the_nazgul_range(
            remaining_will=20,
            distance_inches=-1,
        )

def test_master_of_the_nazgul_gives_plus_one_inside_range():
    result = (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=20,
            distance_inches=18,
        )
    )

    assert result == 1


def test_master_of_the_nazgul_gives_no_bonus_outside_range():
    result = (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=20,
            distance_inches=18.1,
        )
    )

    assert result == 0


def test_master_bonus_uses_twelve_inch_middle_band():
    assert (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=10,
            distance_inches=12,
        )
        == 1
    )

    assert (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=10,
            distance_inches=12.1,
        )
        == 0
    )


def test_master_bonus_uses_six_inch_low_will_band():
    assert (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=9,
            distance_inches=6,
        )
        == 1
    )

    assert (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=9,
            distance_inches=6.1,
        )
        == 0
    )