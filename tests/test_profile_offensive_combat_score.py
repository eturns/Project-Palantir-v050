import pytest

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from profile_offensive_combat_score import (
    calculate_profile_offensive_combat_score,
)
from profiles import Profile


def create_profile(
    *,
    fight: int,
    strength: int,
    attacks: int,
) -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=0,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=strength,
        defence=5,
        attacks=attacks,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_profile_offensive_combat_score_combines_duel_and_wound_probability():
    profile = create_profile(
        fight=4,
        strength=4,
        attacks=1,
    )

    score = calculate_profile_offensive_combat_score(
        profile,
        DEFAULT_COMBAT_BENCHMARK,
    )

    # F4 A1 vs F4 A1:
    # Duel win probability = 0.5
    #
    # S4 vs D6:
    # wound probability = 1/3
    #
    # 1 strike:
    # expected wounds after winning = 1/3
    #
    # offensive score = 0.5 * 1/3 = 1/6
    assert score == pytest.approx(
        1 / 6,
    )


def test_more_attacks_improve_offensive_combat_score():
    one_attack = create_profile(
        fight=4,
        strength=4,
        attacks=1,
    )

    two_attacks = create_profile(
        fight=4,
        strength=4,
        attacks=2,
    )

    one_attack_score = (
        calculate_profile_offensive_combat_score(
            one_attack,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    two_attack_score = (
        calculate_profile_offensive_combat_score(
            two_attacks,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert two_attack_score > one_attack_score


def test_strength_improves_offensive_score_when_wound_target_improves():
    strength_four = create_profile(
        fight=4,
        strength=4,
        attacks=1,
    )

    strength_six = create_profile(
        fight=4,
        strength=6,
        attacks=1,
    )

    strength_four_score = (
        calculate_profile_offensive_combat_score(
            strength_four,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    strength_six_score = (
        calculate_profile_offensive_combat_score(
            strength_six,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert strength_six_score > strength_four_score

def test_offensive_combat_score_is_bounded_at_one():
    profile = create_profile(
        fight=10,
        strength=10,
        attacks=3,
    )

    score = calculate_profile_offensive_combat_score(
        profile,
        DEFAULT_COMBAT_BENCHMARK,
    )

    assert 0.0 <= score <= 1.0