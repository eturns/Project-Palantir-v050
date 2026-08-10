import pytest

from configured_profile import ConfiguredProfile
from profiles import Profile
from wargear import Wargear
from slayer_of_men import (
    calculate_slayer_of_men_duel_probability,
    is_slayer_of_men_burly_active,
)

def create_test_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name="Test Profile",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
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

def test_slayer_is_burly_within_one_inch():
    assert is_slayer_of_men_burly_active(
        distance_to_other_slayer_inches=1,
    )


def test_slayer_is_not_burly_beyond_one_inch():
    assert not is_slayer_of_men_burly_active(
        distance_to_other_slayer_inches=1.01,
    )


def test_slayer_burly_range_rejects_negative_distance():
    with pytest.raises(
        ValueError,
        match="Distance to other Slayer cannot be negative.",
    ):
        is_slayer_of_men_burly_active(
            distance_to_other_slayer_inches=-0.1,
        )

def test_slayer_pair_within_one_inch_removes_duel_penalty():
    attacker_profile = create_test_profile(
        "SLAYER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    attacker_profile.default_wargear.append(
        Wargear(
            id="WG_TWO_HANDED_WEAPON",
            name="Two-handed Weapon",
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_slayer_of_men_duel_probability(
        attacker=attacker,
        defender=defender,
        distance_to_other_slayer_inches=1,
    )

    assert result.attacker_win_probability == 0.5