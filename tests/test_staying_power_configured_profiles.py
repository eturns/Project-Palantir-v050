import pytest

from army import Army
from combat_benchmark import CombatBenchmark
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from profile_option import ProfileOption
from profiles import Profile
from staying_power_capability import (
    calculate_army_staying_power,
    calculate_staying_power_from_profile,
)


def create_profile():
    return Profile(
        id="GENERIC_HERO",
        name="Generic Hero",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="6+",
        might=2,
        will=1,
        fate=1,
        max_in_army=0,
    )


def create_benchmark():
    return CombatBenchmark(
        fight=4,
        strength=3,
        defence=5,
        attacks=2,
        wounds=2,
    )


def create_shield_option():
    return ProfileOption(
        id="SHIELD",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )


def test_configured_defence_changes_profile_staying_power():
    profile = create_profile()

    shield_option = create_shield_option()

    profile.profile_options.append(
        shield_option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    shielded = ConfiguredProfile(
        profile=profile,
        selected_options=(
            shield_option,
        ),
    )

    plain_score = calculate_staying_power_from_profile(
        plain,
        create_benchmark(),
    )

    shielded_score = calculate_staying_power_from_profile(
        shielded,
        create_benchmark(),
    )

    assert plain.effective_defence == 5
    assert shielded.effective_defence == 6

    assert shielded_score > plain_score


def test_staying_power_preserves_base_profile_compatibility():
    profile = create_profile()

    base_score = calculate_staying_power_from_profile(
        profile,
        create_benchmark(),
    )

    configured_score = (
        calculate_staying_power_from_profile(
            ConfiguredProfile(
                profile=profile,
            ),
            create_benchmark(),
        )
    )

    assert base_score == pytest.approx(
        configured_score,
    )


def test_configured_defence_does_not_change_wound_capacity():
    profile = create_profile()

    shield_option = create_shield_option()

    profile.profile_options.append(
        shield_option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    shielded = ConfiguredProfile(
        profile=profile,
        selected_options=(
            shield_option,
        ),
    )

    # Both configurations still have the same
    # intrinsic Wounds characteristic.
    assert plain.profile.wounds == 2
    assert shielded.profile.wounds == 2

    # With 2 Wounds, wound capacity remains 0.5
    # for both configurations.
    #
    # Any difference in staying power must therefore
    # come from configured Defence.
    plain_score = calculate_staying_power_from_profile(
        plain,
        create_benchmark(),
    )

    shielded_score = calculate_staying_power_from_profile(
        shielded,
        create_benchmark(),
    )

    assert shielded_score > plain_score


def test_army_staying_power_distinguishes_two_configurations_of_same_profile():
    profile = create_profile()

    shield_option = create_shield_option()

    profile.profile_options.append(
        shield_option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    shielded = ConfiguredProfile(
        profile=profile,
        selected_options=(
            shield_option,
        ),
    )

    army = Army()

    army.add_configured_profile(
        plain,
    )

    army.add_configured_profile(
        shielded,
    )

    benchmark = create_benchmark()

    result = calculate_army_staying_power(
        army,
        benchmark,
    )

    plain_score = calculate_staying_power_from_profile(
        plain,
        benchmark,
    )

    shielded_score = calculate_staying_power_from_profile(
        shielded,
        benchmark,
    )

    expected = (
        plain_score
        + shielded_score
    ) / 2

    assert len(army.entries) == 2

    assert (
        army.entries[0].profile
        is army.entries[1].profile
    )

    assert result == pytest.approx(
        expected,
    )