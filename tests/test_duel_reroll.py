from duel_reroll import DuelReroll
from duel_probability import (apply_standard_duel_reroll, 
                              generate_standard_reroll_outcomes, 
                              generate_duel_roll_outcomes, 
                              calculate_raw_duel_probability, 
                              calculate_basic_duel_probability,
                              calculate_profile_duel_probability,)
from profiles import Profile

def test_duel_reroll_defaults_to_unavailable():
    reroll = DuelReroll()

    assert reroll.available is False


def test_duel_reroll_can_be_available():
    reroll = DuelReroll(available=True)

    assert reroll.available is True


def test_standard_reroll_replaces_lowest_die():
    result = apply_standard_duel_reroll(
        rolls=(2, 5, 4),
        replacement_roll=6,
    )

    assert result == (6, 5, 4)


def test_standard_reroll_replaces_first_lowest_die_on_tie():
    result = apply_standard_duel_reroll(
        rolls=(2, 5, 2),
        replacement_roll=4,
    )

    assert result == (4, 5, 2)


def test_standard_reroll_rejects_empty_rolls():
    try:
        apply_standard_duel_reroll(
            rolls=(),
            replacement_roll=4,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty Duel rolls.")


def test_standard_reroll_rejects_invalid_replacement_roll():
    try:
        apply_standard_duel_reroll(
            rolls=(2, 5, 4),
            replacement_roll=7,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for invalid replacement Duel roll."
        )

def test_generate_standard_reroll_outcomes_returns_six_results():
    outcomes = generate_standard_reroll_outcomes((2, 5, 4))

    assert len(outcomes) == 6


def test_generate_standard_reroll_outcomes_replaces_lowest_die():
    outcomes = generate_standard_reroll_outcomes((2, 5, 4))

    assert outcomes == (
        (1, 5, 4),
        (2, 5, 4),
        (3, 5, 4),
        (4, 5, 4),
        (5, 5, 4),
        (6, 5, 4),
    )

def test_generate_duel_roll_outcomes_without_reroll():
    outcomes = generate_duel_roll_outcomes(
        attacks=1,
        reroll_available=False,
    )

    assert outcomes == (
        (1,),
        (2,),
        (3,),
        (4,),
        (5,),
        (6,),
    )


def test_generate_duel_roll_outcomes_with_reroll():
    outcomes = generate_duel_roll_outcomes(
        attacks=1,
        reroll_available=True,
    )

    assert len(outcomes) == 36


def test_generate_duel_roll_outcomes_rejects_zero_attacks():
    try:
        generate_duel_roll_outcomes(attacks=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for zero Duel dice.")

def test_raw_duel_with_attacker_reroll_improves_attacker_result():
    without_reroll = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
    )

    with_reroll = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        attacker_reroll_available=True,
    )

    assert (
        with_reroll.attacker_win_probability
        > without_reroll.attacker_win_probability
    )


def test_raw_duel_with_equal_rerolls_is_symmetric():
    result = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        attacker_reroll_available=True,
        defender_reroll_available=True,
    )

    assert result.attacker_win_probability == result.defender_win_probability

def test_standard_reroll_is_not_used_when_roll_contains_six():
    outcomes = generate_standard_reroll_outcomes((2, 6, 4))

    assert outcomes == (
        (2, 6, 4),
        (2, 6, 4),
        (2, 6, 4),
        (2, 6, 4),
        (2, 6, 4),
        (2, 6, 4),
    )

def test_basic_duel_supports_attacker_reroll():
    without_reroll = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
    )

    with_reroll = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_reroll_available=True,
    )

    assert (
        with_reroll.attacker_win_probability
        > without_reroll.attacker_win_probability
    )

    assert with_reroll.draw_probability == 0.0

def test_profile_duel_supports_attacker_reroll():
    attacker = Profile(
        id="ATTACKER",
        name="Attacker",
        points=0,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    defender = Profile(
        id="DEFENDER",
        name="Defender",
        points=0,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    without_reroll = calculate_profile_duel_probability(
        attacker,
        defender,
    )

    with_reroll = calculate_profile_duel_probability(
        attacker,
        defender,
        attacker_reroll_available=True,
    )

    assert (
        with_reroll.attacker_win_probability
        > without_reroll.attacker_win_probability
    )

def test_basic_duel_supports_defender_reroll():
    without_reroll = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
    )

    with_reroll = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        defender_reroll_available=True,
    )

    assert (
        with_reroll.defender_win_probability
        > without_reroll.defender_win_probability
    )

    assert with_reroll.draw_probability == 0.0


def test_basic_duel_with_both_rerolls_is_symmetric():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_reroll_available=True,
        defender_reroll_available=True,
    )

    assert result.attacker_win_probability == result.defender_win_probability
    assert result.draw_probability == 0.0