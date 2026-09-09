import pytest

from army import Army
from army_combat_capability import (
    calculate_army_combat_capability,
)
from combat_benchmark import CombatBenchmark
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from profile_combat_capability import (
    calculate_profile_combat_capability,
)
from profile_option import ProfileOption
from profiles import Profile


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


def test_configured_defence_changes_profile_combat_capability():
    profile = create_profile()

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

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

    plain_score = calculate_profile_combat_capability(
        plain,
        create_benchmark(),
    )

    shielded_score = calculate_profile_combat_capability(
        shielded,
        create_benchmark(),
    )

    assert plain.effective_defence == 5
    assert shielded.effective_defence == 6

    assert shielded_score > plain_score


def test_profile_combat_capability_preserves_base_profile_compatibility():
    profile = create_profile()

    score = calculate_profile_combat_capability(
        profile,
        create_benchmark(),
    )

    configured_score = (
        calculate_profile_combat_capability(
            ConfiguredProfile(
                profile=profile,
            ),
            create_benchmark(),
        )
    )

    assert score == pytest.approx(
        configured_score,
    )


def test_army_combat_capability_distinguishes_two_configurations_of_same_profile():
    profile = create_profile()

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

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

    plain_army = Army()
    plain_army.add_configured_profile(
        plain,
    )

    shielded_army = Army()
    shielded_army.add_configured_profile(
        shielded,
    )

    benchmark = create_benchmark()

    plain_score = calculate_army_combat_capability(
        plain_army,
        benchmark,
    )

    shielded_score = calculate_army_combat_capability(
        shielded_army,
        benchmark,
    )

    assert (
        plain_army.entries[0].profile
        is shielded_army.entries[0].profile
    )

    assert shielded_score > plain_score


def test_mixed_army_preserves_same_profile_different_loadouts():
    profile = create_profile()

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

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

    mixed_score = calculate_army_combat_capability(
        army,
        benchmark,
    )

    plain_score = calculate_profile_combat_capability(
        plain,
        benchmark,
    )

    shielded_score = calculate_profile_combat_capability(
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

    assert mixed_score == pytest.approx(
        expected,
    )