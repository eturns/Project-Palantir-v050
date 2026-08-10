from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from configured_wound_probability import (
    calculate_configured_wound_probability,
)
from configured_profile import ConfiguredProfile
from profiles import Profile


def create_test_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name="Test Profile",
        points=0,
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


def test_combat_api_duel_entry_point_returns_probability_result():
    attacker = ConfiguredProfile(
        profile=create_test_profile("ATTACKER"),
    )
    defender = ConfiguredProfile(
        profile=create_test_profile("DEFENDER"),
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
    )

    assert isinstance(
        result.attacker_win_probability,
        float,
    )
    assert isinstance(
        result.defender_win_probability,
        float,
    )


def test_combat_api_wound_entry_point_is_importable():
    assert callable(
        calculate_configured_wound_probability
    )