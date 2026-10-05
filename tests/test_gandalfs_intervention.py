import pytest

from gandalfs_intervention import (
    resolve_shattered_spirit_with_gandalf,
)
from shattered_spirit_state import (
    ShatteredSpiritResult,
)


def test_gandalf_can_turn_success_into_double():
    state = resolve_shattered_spirit_with_gandalf(
        first_die=2,
        second_die=3,
        intelligence="5+",
        within_three_inches_of_friendly_gandalf=True,
        die_to_adjust=1,
        adjustment=1,
    )

    assert (
        state.result
        is ShatteredSpiritResult.EMPOWERED
    )


def test_gandalf_can_turn_failure_into_success():
    state = resolve_shattered_spirit_with_gandalf(
        first_die=2,
        second_die=3,
        intelligence="6+",
        within_three_inches_of_friendly_gandalf=True,
        die_to_adjust=1,
        adjustment=1,
    )

    assert (
        state.result
        is ShatteredSpiritResult.EMPOWERED
    )


def test_gandalf_can_adjust_down():
    state = resolve_shattered_spirit_with_gandalf(
        first_die=4,
        second_die=3,
        intelligence="6+",
        within_three_inches_of_friendly_gandalf=True,
        die_to_adjust=1,
        adjustment=-1,
    )

    assert (
        state.result
        is ShatteredSpiritResult.EMPOWERED
    )


def test_gandalf_intervention_is_optional():
    state = resolve_shattered_spirit_with_gandalf(
        first_die=2,
        second_die=4,
        intelligence="6+",
        within_three_inches_of_friendly_gandalf=True,
    )

    assert (
        state.result
        is ShatteredSpiritResult.NORMAL
    )


def test_cannot_adjust_without_nearby_friendly_gandalf():
    with pytest.raises(
        ValueError,
        match="cannot be used",
    ):
        resolve_shattered_spirit_with_gandalf(
            first_die=2,
            second_die=3,
            intelligence="6+",
            within_three_inches_of_friendly_gandalf=False,
            die_to_adjust=1,
            adjustment=1,
        )


def test_rejects_adjusting_below_one():
    with pytest.raises(
        ValueError,
        match="Adjusted first die",
    ):
        resolve_shattered_spirit_with_gandalf(
            first_die=1,
            second_die=4,
            intelligence="6+",
            within_three_inches_of_friendly_gandalf=True,
            die_to_adjust=1,
            adjustment=-1,
        )


def test_rejects_adjusting_above_six():
    with pytest.raises(
        ValueError,
        match="Adjusted second die",
    ):
        resolve_shattered_spirit_with_gandalf(
            first_die=2,
            second_die=6,
            intelligence="6+",
            within_three_inches_of_friendly_gandalf=True,
            die_to_adjust=2,
            adjustment=1,
        )