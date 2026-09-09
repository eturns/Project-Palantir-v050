import pytest

from army import Army
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from matchup_evaluator import calculate_matchup_result
from optimiser_candidate import OptimiserCandidate
from profile_option import ProfileOption
from profiles import Profile


def create_profile(
    *,
    profile_id: str,
    defence: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=defence,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="6+",
        might=2,
        will=1,
        fate=1,
        max_in_army=0,
    )


def create_target():
    return Profile(
        id="TARGET",
        name="Target",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_matchup_defensive_score_uses_configured_defence():
    profile = create_profile(
        profile_id="GENERIC_HERO",
        defence=5,
    )

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

    plain_candidate = OptimiserCandidate(
        army=plain_army,
    )

    shielded_candidate = OptimiserCandidate(
        army=shielded_army,
    )

    target = create_target()

    plain_result = calculate_matchup_result(
        candidate=plain_candidate,
        target_profile=target,
    )

    shielded_result = calculate_matchup_result(
        candidate=shielded_candidate,
        target_profile=target,
    )

    assert plain.effective_defence == 5
    assert shielded.effective_defence == 6

    assert (
        shielded_result.defensive_score
        > plain_result.defensive_score
    )

    assert (
        shielded_result.offensive_score
        == pytest.approx(
            plain_result.offensive_score,
        )
    )

    assert (
        shielded_result.score
        > plain_result.score
    )


def test_matchup_preserves_two_configurations_of_same_profile():
    profile = create_profile(
        profile_id="GENERIC_HERO",
        defence=5,
    )

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

    candidate = OptimiserCandidate(
        army=army,
    )

    result = calculate_matchup_result(
        candidate=candidate,
        target_profile=create_target(),
    )

    plain_only = Army()
    plain_only.add_configured_profile(
        plain,
    )

    shielded_only = Army()
    shielded_only.add_configured_profile(
        shielded,
    )

    plain_result = calculate_matchup_result(
        candidate=OptimiserCandidate(
            army=plain_only,
        ),
        target_profile=create_target(),
    )

    shielded_result = calculate_matchup_result(
        candidate=OptimiserCandidate(
            army=shielded_only,
        ),
        target_profile=create_target(),
    )

    expected_defensive_score = (
        plain_result.defensive_score
        + shielded_result.defensive_score
    ) / 2

    assert len(army.entries) == 2

    assert (
        army.entries[0].profile
        is army.entries[1].profile
    )

    assert (
        result.defensive_score
        == pytest.approx(
            expected_defensive_score,
        )
    )