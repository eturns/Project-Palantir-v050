from fractions import Fraction

import pytest

from shooting_hit_probability import (
    get_shooting_hit_probability,
    parse_shoot_value,
)
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from profile_option import ProfileOption
from profiles import Profile
from shooting_hit_probability import (
    get_shooting_hit_probability,
    get_shooting_hit_probability_for_profile,
    parse_shoot_value,
)

@pytest.mark.parametrize(
    ("shoot_value", "expected"),
    (
        ("2+", 2),
        ("3+", 3),
        ("4+", 4),
        ("5+", 5),
        ("6+", 6),
    ),
)
def test_parse_shoot_value_returns_required_roll(
    shoot_value,
    expected,
):
    assert parse_shoot_value(shoot_value) == expected


@pytest.mark.parametrize(
    "shoot_value",
    (
        "",
        "4",
        "+4",
        "abc",
        "7+",
        "1+",
    ),
)
def test_parse_shoot_value_rejects_invalid_notation(
    shoot_value,
):
    with pytest.raises(ValueError):
        parse_shoot_value(shoot_value)


@pytest.mark.parametrize(
    ("shoot_value", "expected"),
    (
        ("2+", Fraction(5, 6)),
        ("3+", Fraction(4, 6)),
        ("4+", Fraction(3, 6)),
        ("5+", Fraction(2, 6)),
        ("6+", Fraction(1, 6)),
    ),
)
def test_shooting_hit_probability_uses_shoot_value(
    shoot_value,
    expected,
):
    assert (
        get_shooting_hit_probability(shoot_value)
        == expected
    )

def create_test_shooter(
    *,
    shooting: str = "4+",
) -> Profile:
    return Profile(
        id="TEST_SHOOTER",
        name="Test Shooter",
        points=10,
        movement=6,
        fight=3,
        shooting=shooting,
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_configured_profile_uses_effective_shooting_value():
    profile = create_test_shooter(
        shooting="4+",
    )

    option = ProfileOption(
        id="TEST_SHOOTING_OVERRIDE",
        name="Improved Shoot",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                shooting_override="3+",
            ),
        ),
    )

    profile.profile_options.append(option)

    configured = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert (
        get_shooting_hit_probability_for_profile(
            configured,
        )
        == Fraction(4, 6)
    )


def test_configured_profile_without_override_uses_base_shooting():
    profile = create_test_shooter(
        shooting="4+",
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert (
        get_shooting_hit_probability_for_profile(
            configured,
        )
        == Fraction(3, 6)
    )

@pytest.mark.parametrize(
    ("shoot_value", "modifier", "expected"),
    (
        ("4+", 0, Fraction(3, 6)),
        ("4+", 1, Fraction(4, 6)),
        ("4+", -1, Fraction(2, 6)),
        ("3+", 1, Fraction(5, 6)),
        ("5+", -1, Fraction(1, 6)),
    ),
)
def test_shooting_hit_probability_applies_modifier(
    shoot_value,
    modifier,
    expected,
):
    assert (
        get_shooting_hit_probability(
            shoot_value,
            modifier=modifier,
        )
        == expected
    )

def test_configured_profile_hit_probability_applies_modifier():
    profile = create_test_shooter(
        shooting="4+",
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert (
        get_shooting_hit_probability_for_profile(
            configured,
            modifier=1,
        )
        == Fraction(4, 6)
    )

@pytest.mark.parametrize(
    ("shoot_value", "modifier", "expected"),
    (
        ("2+", 1, Fraction(1, 1)),
        ("2+", 5, Fraction(1, 1)),
        ("6+", -1, Fraction(0, 1)),
        ("6+", -5, Fraction(0, 1)),
    ),
)
def test_shooting_hit_probability_clamps_extreme_modifiers(
    shoot_value,
    modifier,
    expected,
):
    assert (
        get_shooting_hit_probability(
            shoot_value,
            modifier=modifier,
        )
        == expected
    )