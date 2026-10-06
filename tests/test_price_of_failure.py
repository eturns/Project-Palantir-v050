import pytest

from price_of_failure import (
    _duel_roll_wins,
    apply_price_of_failure_reroll,
    calculate_price_of_failure_duel_probability,
    choose_optimal_price_of_failure_reroll_indexes,
    choose_price_of_failure_reroll_indexes,
    generate_price_of_failure_reroll_index_choices,
    generate_price_of_failure_reroll_outcomes,
)
from itertools import (
    combinations,
)
from price_of_failure_state import (
    PriceOfFailureState,
)

from duel_modifier import DuelModifier

def test_price_of_failure_can_reroll_one_selected_die():
    result = apply_price_of_failure_reroll(
        rolls=(2, 5, 3),
        reroll_indexes=(0,),
        replacement_rolls=(6,),
    )

    assert result == (
        6,
        5,
        3,
    )


def test_price_of_failure_can_reroll_multiple_selected_dice():
    result = apply_price_of_failure_reroll(
        rolls=(2, 5, 3),
        reroll_indexes=(0, 2),
        replacement_rolls=(6, 4),
    )

    assert result == (
        6,
        5,
        4,
    )


def test_price_of_failure_preserves_unselected_dice():
    result = apply_price_of_failure_reroll(
        rolls=(1, 6, 2),
        reroll_indexes=(0, 2),
        replacement_rolls=(4, 5),
    )

    assert result[1] == 6


def test_price_of_failure_one_rerolled_die_has_six_outcomes():
    outcomes = (
        generate_price_of_failure_reroll_outcomes(
            rolls=(2, 5),
            reroll_indexes=(0,),
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=True,
            ),
        )
    )

    assert len(outcomes) == 6


def test_price_of_failure_two_rerolled_dice_have_36_outcomes():
    outcomes = (
        generate_price_of_failure_reroll_outcomes(
            rolls=(2, 3, 6),
            reroll_indexes=(0, 1),
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=True,
            ),
        )
    )

    assert len(outcomes) == 36


def test_price_of_failure_does_nothing_when_not_eligible():
    outcomes = (
        generate_price_of_failure_reroll_outcomes(
            rolls=(2, 3),
            reroll_indexes=(0, 1),
            state=PriceOfFailureState(
                declared=False,
                within_azog_range=True,
            ),
        )
    )

    assert outcomes == (
        (2, 3),
    )


def test_price_of_failure_rejects_duplicate_reroll_indexes():
    with pytest.raises(
        ValueError,
        match="cannot be rerolled twice",
    ):
        apply_price_of_failure_reroll(
            rolls=(2, 3),
            reroll_indexes=(0, 0),
            replacement_rolls=(4, 5),
        )

def test_price_of_failure_keeps_single_highest_die():
    indexes = (
        choose_price_of_failure_reroll_indexes(
            (2, 5, 3),
        )
    )

    assert indexes == (
        0,
        2,
    )


def test_price_of_failure_keeps_one_of_equal_highest_dice():
    indexes = (
        choose_price_of_failure_reroll_indexes(
            (5, 5, 2),
        )
    )

    assert indexes == (
        1,
        2,
    )


def test_price_of_failure_does_not_reroll_when_six_is_present():
    indexes = (
        choose_price_of_failure_reroll_indexes(
            (2, 6, 3),
        )
    )

    assert indexes == ()


def test_price_of_failure_single_die_has_nothing_to_reroll():
    indexes = (
        choose_price_of_failure_reroll_indexes(
            (4,),
        )
    )

    assert indexes == ()

def generate_price_of_failure_reroll_index_choices(
    rolls: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    if not rolls:
        raise ValueError(
            "At least one Duel die is required."
        )

    indexes = tuple(
        range(len(rolls))
    )

    return tuple(
        choice
        for reroll_count in range(
            len(indexes) + 1
        )
        for choice in combinations(
            indexes,
            reroll_count,
        )
    )

def calculate_price_of_failure_choice_win_probability(
    *,
    attacker_rolls: tuple[int, ...],
    defender_rolls: tuple[int, ...],
    reroll_indexes: tuple[int, ...],
    attacker_fight: int,
    defender_fight: int,
    attacker_roll_off_probability: float = 0.5,
) -> float:
    if not 0.0 <= attacker_roll_off_probability <= 1.0:
        raise ValueError(
            "Attacker roll-off probability must be "
            "between 0 and 1."
        )

    state = PriceOfFailureState(
        declared=True,
        within_azog_range=True,
    )

    outcomes = (
        generate_price_of_failure_reroll_outcomes(
            rolls=attacker_rolls,
            reroll_indexes=reroll_indexes,
            state=state,
        )
    )

    return sum(
        _duel_roll_wins(
            attacker_rolls=outcome,
            defender_rolls=defender_rolls,
            attacker_fight=attacker_fight,
            defender_fight=defender_fight,
            attacker_roll_off_probability=(
                attacker_roll_off_probability
            ),
        )
        for outcome in outcomes
    ) / len(outcomes)


def choose_optimal_price_of_failure_reroll_indexes(
    *,
    attacker_rolls: tuple[int, ...],
    defender_rolls: tuple[int, ...],
    attacker_fight: int,
    defender_fight: int,
    attacker_roll_off_probability: float = 0.5,
) -> tuple[int, ...]:
    choices = (
        generate_price_of_failure_reroll_index_choices(
            attacker_rolls
        )
    )

    return max(
        choices,
        key=lambda choice: (
            calculate_price_of_failure_choice_win_probability(
                attacker_rolls=attacker_rolls,
                defender_rolls=defender_rolls,
                reroll_indexes=choice,
                attacker_fight=attacker_fight,
                defender_fight=defender_fight,
                attacker_roll_off_probability=(
                    attacker_roll_off_probability
                ),
            ),
            -len(choice),
        ),
    )

def test_price_of_failure_generates_every_possible_reroll_subset():
    choices = (
        generate_price_of_failure_reroll_index_choices(
            (2, 4),
        )
    )

    assert set(choices) == {
        (),
        (0,),
        (1,),
        (0, 1),
    }


def test_price_of_failure_keeps_winning_roll_when_already_ahead():
    choice = (
        choose_optimal_price_of_failure_reroll_indexes(
            attacker_rolls=(6, 2),
            defender_rolls=(5,),
            attacker_fight=5,
            defender_fight=5,
        )
    )

    assert choice == ()


def test_price_of_failure_rerolls_lower_die_when_highest_is_useful():
    choice = (
        choose_optimal_price_of_failure_reroll_indexes(
            attacker_rolls=(5, 2),
            defender_rolls=(4,),
            attacker_fight=5,
            defender_fight=5,
        )
    )

    assert choice == ()


def test_price_of_failure_can_reroll_all_dice_when_opponent_has_six():
    choice = (
        choose_optimal_price_of_failure_reroll_indexes(
            attacker_rolls=(5, 2),
            defender_rolls=(6,),
            attacker_fight=5,
            defender_fight=5,
        )
    )

    assert choice == (
        0,
        1,
    )


def test_price_of_failure_respects_superior_fight_on_equal_roll():
    choice = (
        choose_optimal_price_of_failure_reroll_indexes(
            attacker_rolls=(5, 2),
            defender_rolls=(5,),
            attacker_fight=5,
            defender_fight=4,
        )
    )

    assert choice == ()

def test_price_of_failure_duel_probability_sums_to_one():
    result = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=True,
            ),
        )
    )

    assert (
        result.attacker_win_probability
        + result.defender_win_probability
        + result.draw_probability
    ) == pytest.approx(1.0)


def test_price_of_failure_improves_duel_win_probability():
    without_rule = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=False,
                within_azog_range=True,
            ),
        )
    )

    with_rule = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=True,
            ),
        )
    )

    assert (
        with_rule.attacker_win_probability
        > without_rule.attacker_win_probability
    )


def test_price_of_failure_has_no_effect_out_of_range():
    unavailable = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=False,
            ),
        )
    )

    undeclared = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=False,
                within_azog_range=True,
            ),
        )
    )

    assert unavailable == undeclared


def test_price_of_failure_resolves_equal_fight_by_roll_off():
    result = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=1,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=False,
                within_azog_range=True,
            ),
            attacker_roll_off_probability=0.5,
        )
    )

    assert result.attacker_win_probability == pytest.approx(
        0.5
    )
    assert result.defender_win_probability == pytest.approx(
        0.5
    )
    assert result.draw_probability == 0.0


def test_price_of_failure_respects_higher_fight():
    result = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=1,
            attacker_fight=6,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=False,
                within_azog_range=True,
            ),
        )
    )

    assert (
        result.attacker_win_probability
        > 0.5
    )

def test_price_of_failure_respects_attacker_duel_modifier():
    without_modifier = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=True,
            ),
        )
    )

    with_modifier = (
        calculate_price_of_failure_duel_probability(
            attacker_attacks=2,
            attacker_fight=5,
            defender_attacks=1,
            defender_fight=5,
            state=PriceOfFailureState(
                declared=True,
                within_azog_range=True,
            ),
            attacker_modifier=DuelModifier(
                value=-1,
                ignored_on_natural_six=True,
            ),
        )
    )

    assert (
        with_modifier.attacker_win_probability
        < without_modifier.attacker_win_probability
    )


def test_price_of_failure_preserves_natural_six_with_two_handed_modifier():
    result = _duel_roll_wins(
        attacker_rolls=(6,),
        defender_rolls=(5,),
        attacker_fight=5,
        defender_fight=5,
        attacker_roll_off_probability=0.5,
        attacker_modifier=DuelModifier(
            value=-1,
            ignored_on_natural_six=True,
        ),
    )

    assert result == 1.0