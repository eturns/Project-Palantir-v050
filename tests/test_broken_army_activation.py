from fractions import Fraction

from army_model_state import ArmyModelState
from broken_army_activation import (
    calculate_broken_army_activation,
)
from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext
from profiles import Profile


def make_profile(
    courage: str = "7+",
) -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage=courage,
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_unbroken_army_requires_no_courage_test():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    result = calculate_broken_army_activation(
        ArmyModelState(
            starting_models=10,
            remaining_models=6,
        ),
        configured,
    )

    assert result.army_is_broken is False
    assert result.courage_test_required is False
    assert result.flee_probability == Fraction(0, 1)


def test_broken_army_requires_courage_test():
    configured = ConfiguredProfile(
        profile=make_profile(
            courage="7+",
        ),
    )

    result = calculate_broken_army_activation(
        ArmyModelState(
            starting_models=10,
            remaining_models=4,
        ),
        configured,
    )

    assert result.army_is_broken is True
    assert result.courage_test_required is True

    assert (
        result.courage_test_success_probability
        == Fraction(21, 36)
    )

    assert (
        result.flee_probability
        == Fraction(15, 36)
    )


def test_model_that_cannot_activate_does_not_test():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    result = calculate_broken_army_activation(
        ArmyModelState(
            starting_models=10,
            remaining_models=4,
        ),
        configured,
        can_activate=False,
    )

    assert result.army_is_broken is True
    assert result.courage_test_required is False
    assert result.flee_probability == Fraction(0, 1)


def test_stand_fast_forces_broken_army_courage_pass():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    result = calculate_broken_army_activation(
        ArmyModelState(
            starting_models=10,
            remaining_models=4,
        ),
        configured,
        receives_stand_fast=True,
    )

    assert result.courage_test_required is True
    assert (
        result.courage_test_success_probability
        == Fraction(1, 1)
    )
    assert result.flee_probability == Fraction(0, 1)


def test_automatic_pass_context_forces_broken_army_courage_pass():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    result = calculate_broken_army_activation(
        ArmyModelState(
            starting_models=10,
            remaining_models=4,
        ),
        configured,
        courage_test_context=CourageTestContext(
            automatically_passes=True,
        ),
    )

    assert result.courage_test_required is True
    assert (
        result.courage_test_success_probability
        == Fraction(1, 1)
    )
    assert result.flee_probability == Fraction(0, 1)