import pytest

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profiles import Profile


def create_profile(
    *,
    fight: int,
    defence: int,
    attacks: int,
) -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=0,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=4,
        defence=defence,
        attacks=attacks,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_profile_defensive_combat_score_reflects_resistance_to_benchmark():
    profile = create_profile(
        fight=4,
        defence=6,
        attacks=1,
    )

    score = calculate_profile_defensive_combat_score(
        profile,
        DEFAULT_COMBAT_BENCHMARK,
    )

    # Benchmark F4 A1 vs profile F4 A1:
    # benchmark wins Duel = 0.5
    #
    # Benchmark S4 vs D6:
    # wound probability = 1/3
    #
    # expected incoming wound probability = 1/6
    #
    # defensive score = 1 - 1/6
    assert score == pytest.approx(
        5 / 6,
    )


def test_higher_defence_improves_defensive_combat_score():
    defence_five = create_profile(
        fight=4,
        defence=5,
        attacks=1,
    )

    defence_seven = create_profile(
        fight=4,
        defence=7,
        attacks=1,
    )

    defence_five_score = (
        calculate_profile_defensive_combat_score(
            defence_five,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    defence_seven_score = (
        calculate_profile_defensive_combat_score(
            defence_seven,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert defence_seven_score > defence_five_score


def test_more_attacks_improve_defensive_combat_score_through_duel_resistance():
    one_attack = create_profile(
        fight=4,
        defence=6,
        attacks=1,
    )

    two_attacks = create_profile(
        fight=4,
        defence=6,
        attacks=2,
    )

    one_attack_score = (
        calculate_profile_defensive_combat_score(
            one_attack,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    two_attack_score = (
        calculate_profile_defensive_combat_score(
            two_attacks,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert two_attack_score > one_attack_score