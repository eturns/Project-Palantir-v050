from duel_probability import (
    calculate_basic_duel_probability,
    calculate_duel_probability,
    calculate_profile_duel_probability,
    calculate_raw_duel_probability,
    generate_duel_roll_outcomes,
    generate_standard_reroll_outcomes,
    resolve_draw_probability_by_roll_off,
    resolve_duel_rolls_with_might,
    calculate_duel_probability_with_heroic_strike,
)

from duel_probability_result import DuelProbabilityResult
from duel_might import DuelMightStrategy
from profiles import Profile
from duel_modifier import DuelModifier

def test_one_die_vs_one_die():
    result = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
    )

    assert result.attacker_win_probability == 15 / 36
    assert result.defender_win_probability == 15 / 36
    assert result.draw_probability == 6 / 36


def test_probabilities_sum_to_one():
    result = calculate_raw_duel_probability(
        attacker_attacks=2,
        defender_attacks=1,
    )

    total_probability = (
        result.attacker_win_probability
        + result.defender_win_probability
        + result.draw_probability
    )

    assert abs(total_probability - 1.0) < 1e-12


def test_zero_attacker_dice_is_rejected():
    try:
        calculate_raw_duel_probability(
            attacker_attacks=0,
            defender_attacks=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for zero attacker dice."
        )

def test_higher_attacker_fight_wins_drawn_rolls():
    result = calculate_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=4,
    )

    assert result.attacker_win_probability == 21 / 36
    assert result.defender_win_probability == 15 / 36
    assert result.draw_probability == 0.0


def test_higher_defender_fight_wins_drawn_rolls():
    result = calculate_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=5,
    )

    assert result.attacker_win_probability == 15 / 36
    assert result.defender_win_probability == 21 / 36
    assert result.draw_probability == 0.0


def test_equal_fight_keeps_draw_probability():
    result = calculate_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
    )

    assert result.attacker_win_probability == 15 / 36
    assert result.defender_win_probability == 15 / 36
    assert result.draw_probability == 6 / 36


def test_equal_fight_draw_is_split_by_standard_roll_off():
    unresolved_result = calculate_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
    )
def test_custom_roll_off_probability():
    unresolved_result = DuelProbabilityResult(
        attacker_win_probability=0.4,
        defender_win_probability=0.4,
        draw_probability=0.2,
    )

    result = resolve_draw_probability_by_roll_off(
        unresolved_result,
        attacker_roll_off_probability=0.75,
    )

    assert result.attacker_win_probability == 0.55
    assert result.defender_win_probability == 0.45
    assert result.draw_probability == 0.0


def test_invalid_roll_off_probability_is_rejected():
    unresolved_result = DuelProbabilityResult(
        attacker_win_probability=0.4,
        defender_win_probability=0.4,
        draw_probability=0.2,
    )

    try:
        resolve_draw_probability_by_roll_off(
            unresolved_result,
            attacker_roll_off_probability=1.1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for invalid roll-off probability."
        )

def test_basic_duel_resolves_equal_fight_roll_off():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
    )

    assert result.attacker_win_probability == 0.5
    assert result.defender_win_probability == 0.5
    assert result.draw_probability == 0.0


def test_basic_duel_preserves_higher_fight_advantage():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=4,
    )

    assert result.attacker_win_probability == 21 / 36
    assert result.defender_win_probability == 15 / 36
    assert result.draw_probability == 0.0

def test_profile_duel_uses_profile_fight_and_attacks():
    attacker = Profile(
        id="ATTACKER",
        name="Attacker",
        points=0,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
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
        fight=4,
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

    result = calculate_profile_duel_probability(
        attacker,
        defender,
    )

    expected = calculate_basic_duel_probability(
        attacker_attacks=2,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=4,
    )

    assert result == expected

def test_resolve_duel_rolls_with_might_uses_highest_rolls():
    result = resolve_duel_rolls_with_might(
        attacker_rolls=(2, 4, 5),
        defender_rolls=(3, 4),
        attacker_might_available=1,
        defender_might_available=0,
        attacker_might_strategy=DuelMightStrategy.MINIMUM_TO_WIN,
        defender_might_strategy=DuelMightStrategy.NEVER,
    )

    assert result == (5, 4)


def test_resolve_duel_rolls_with_might_can_modify_highest_roll():
    result = resolve_duel_rolls_with_might(
        attacker_rolls=(2, 4),
        defender_rolls=(5,),
        attacker_might_available=2,
        defender_might_available=0,
        attacker_might_strategy=DuelMightStrategy.MINIMUM_TO_WIN,
        defender_might_strategy=DuelMightStrategy.NEVER,
    )

    assert result == (6, 5)


def test_resolve_duel_rolls_with_might_rejects_empty_attacker_rolls():
    try:
        resolve_duel_rolls_with_might(
            attacker_rolls=(),
            defender_rolls=(5,),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty attacker Duel rolls."
        )


def test_resolve_duel_rolls_with_might_rejects_empty_defender_rolls():
    try:
        resolve_duel_rolls_with_might(
            attacker_rolls=(5,),
            defender_rolls=(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty defender Duel rolls."
        )

def test_raw_duel_with_attacker_might_improves_attacker_result():
    without_might = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
    )

    with_might = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        attacker_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert (
        with_might.attacker_win_probability
        > without_might.attacker_win_probability
    )

def test_raw_duel_with_defender_might_improves_defender_result():
    without_might = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
    )

    with_might = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        defender_might_available=1,
        defender_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert (
        with_might.defender_win_probability
        > without_might.defender_win_probability
    )

def test_raw_duel_with_equal_might_is_symmetric():
    result = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        attacker_might_available=1,
        defender_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
        defender_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result.attacker_win_probability == result.defender_win_probability

def test_profile_duel_supports_attacker_might():
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
        might=1,
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

    without_might = calculate_profile_duel_probability(
        attacker,
        defender,
    )

    with_might = calculate_profile_duel_probability(
        attacker,
        defender,
        attacker_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert (
        with_might.attacker_win_probability
        > without_might.attacker_win_probability
    )

def test_duel_applies_reroll_before_might():
    without_reroll = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    with_reroll = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_reroll_available=True,
        attacker_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert (
        with_reroll.attacker_win_probability
        > without_reroll.attacker_win_probability
    )

def test_might_can_create_tie_resolved_by_higher_fight():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=4,
        attacker_might_available=1,
        attacker_might_strategy=(
            DuelMightStrategy.MINIMUM_TO_AVOID_LOSS
        ),
    )

    baseline = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=4,
    )

    assert (
        result.attacker_win_probability
        > baseline.attacker_win_probability
    )

def test_might_created_tie_still_loses_with_lower_fight():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=5,
        attacker_might_available=1,
        attacker_might_strategy=(
            DuelMightStrategy.MINIMUM_TO_AVOID_LOSS
        ),
    )

    baseline = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=5,
    )

    assert (
        result.attacker_win_probability
        == baseline.attacker_win_probability
    )

def test_basic_duel_applies_attacker_might_priority():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_might_available=1,
        defender_might_available=1,
        attacker_might_strategy=(
            DuelMightStrategy.MINIMUM_TO_AVOID_LOSS
        ),
        defender_might_strategy=(
            DuelMightStrategy.MINIMUM_TO_WIN
        ),
    )

    assert result.draw_probability == 0.0
    assert (
        result.defender_win_probability
        > result.attacker_win_probability
    )
def test_raw_duel_rejects_negative_attacker_might():
    try:
        calculate_raw_duel_probability(
            attacker_attacks=1,
            defender_attacks=1,
            attacker_might_available=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for negative attacker Might."
        )


def test_raw_duel_rejects_negative_defender_might():
    try:
        calculate_raw_duel_probability(
            attacker_attacks=1,
            defender_attacks=1,
            defender_might_available=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for negative defender Might."
        )

def test_active_might_strategy_with_zero_might_changes_nothing():
    baseline = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
    )

    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_might_available=0,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result == baseline

def test_heroic_strike_improves_lower_fight_attacker():
    baseline = calculate_duel_probability_with_heroic_strike(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=5,
    )

    with_strike = calculate_duel_probability_with_heroic_strike(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=5,
        attacker_heroic_strike_active=True,
    )

    assert (
        with_strike.attacker_win_probability
        > baseline.attacker_win_probability
    )


def test_equal_heroic_strikes_remain_symmetric():
    result = calculate_duel_probability_with_heroic_strike(
        attacker_attacks=1,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_heroic_strike_active=True,
        defender_heroic_strike_active=True,
    )

    assert result.attacker_win_probability == result.defender_win_probability

def test_profile_duel_supports_attacker_heroic_strike():
    attacker = Profile(
        id="ATTACKER",
        name="Attacker",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=1,
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

    baseline = calculate_profile_duel_probability(
        attacker,
        defender,
    )

    with_strike = calculate_profile_duel_probability(
        attacker,
        defender,
        attacker_heroic_strike_active=True,
    )

    assert (
        with_strike.attacker_win_probability
        > baseline.attacker_win_probability
    )

def test_profile_duel_supports_both_heroic_strikes():
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
        might=1,
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
        might=1,
        will=0,
        fate=0,
        max_in_army=1,
    )

    result = calculate_profile_duel_probability(
        attacker,
        defender,
        attacker_heroic_strike_active=True,
        defender_heroic_strike_active=True,
    )

    assert result.attacker_win_probability == result.defender_win_probability
    assert result.draw_probability == 0.0

def test_generate_duel_roll_outcomes_applies_modifier():
    outcomes = generate_duel_roll_outcomes(
        attacks=1,
        modifier=DuelModifier(
            value=-1,
        ),
    )

    assert outcomes == (
        (1,),
        (1,),
        (2,),
        (3,),
        (4,),
        (5,),
    )


def test_generate_duel_roll_outcomes_preserves_natural_six_exception():
    outcomes = generate_duel_roll_outcomes(
        attacks=1,
        modifier=DuelModifier(
            value=-1,
            ignored_on_natural_six=True,
        ),
    )

    assert outcomes == (
        (1,),
        (1,),
        (2,),
        (3,),
        (4,),
        (6,),
    )

def test_raw_duel_probability_applies_attacker_modifier():
    result = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        attacker_modifier=DuelModifier(
            value=-1,
        ),
    )

    assert result.attacker_win_probability < 5 / 12


def test_raw_duel_probability_applies_defender_modifier():
    result = calculate_raw_duel_probability(
        attacker_attacks=1,
        defender_attacks=1,
        defender_modifier=DuelModifier(
            value=-1,
        ),
    )

    assert result.attacker_win_probability > 5 / 12

def test_duel_probability_applies_attacker_modifier():
    result = calculate_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=4,
        attacker_modifier=DuelModifier(
            value=-1,
        ),
    )

    assert result.attacker_win_probability < 5 / 12


def test_duel_probability_applies_defender_modifier():
    result = calculate_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=4,
        defender_modifier=DuelModifier(
            value=-1,
        ),
    )

    assert result.attacker_win_probability > 5 / 12

def test_basic_duel_probability_applies_attacker_modifier():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=4,
        attacker_modifier=DuelModifier(
            value=-1,
        ),
    )

    assert result.attacker_win_probability < 0.5


def test_basic_duel_probability_applies_defender_modifier():
    result = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=4,
        defender_modifier=DuelModifier(
            value=-1,
        ),
    )

    assert result.attacker_win_probability > 0.5