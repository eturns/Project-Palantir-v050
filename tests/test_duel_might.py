from duel_might import (
    DuelMight,
    DuelMightStrategy,
    apply_might_to_roll,
    calculate_might_needed,
    choose_might_spend,
    resolve_might_modified_roll,
    DuelMightResolution,
    resolve_duel_might,
)

from duel_might import DuelMightStrategy

def test_duel_might_defaults_to_zero():
    might = DuelMight()

    assert might.available == 0


def test_duel_might_can_store_available_points():
    might = DuelMight(available=3)

    assert might.available == 3


def test_duel_might_rejects_negative_value():
    try:
        DuelMight(available=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative Might.")

from duel_might import DuelMight, calculate_might_needed


def test_calculate_might_needed_to_improve_roll():
    result = calculate_might_needed(
        current_roll=4,
        target_roll=6,
    )

    assert result == 2


def test_calculate_might_needed_returns_zero_for_lower_target():
    result = calculate_might_needed(
        current_roll=5,
        target_roll=4,
    )

    assert result == 0


def test_calculate_might_needed_returns_zero_for_equal_target():
    result = calculate_might_needed(
        current_roll=5,
        target_roll=5,
    )

    assert result == 0


def test_calculate_might_needed_rejects_invalid_current_roll():
    try:
        calculate_might_needed(
            current_roll=0,
            target_roll=5,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid current roll.")


def test_calculate_might_needed_rejects_invalid_target_roll():
    try:
        calculate_might_needed(
            current_roll=4,
            target_roll=7,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid target roll.")

def test_apply_might_to_roll_increases_roll():
    result = apply_might_to_roll(
        current_roll=4,
        might_spent=2,
        might_available=3,
    )

    assert result == 6


def test_apply_might_to_roll_allows_zero_spend():
    result = apply_might_to_roll(
        current_roll=5,
        might_spent=0,
        might_available=2,
    )

    assert result == 5


def test_apply_might_to_roll_rejects_overspending():
    try:
        apply_might_to_roll(
            current_roll=4,
            might_spent=2,
            might_available=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for overspending Might.")


def test_apply_might_to_roll_rejects_result_above_six():
    try:
        apply_might_to_roll(
            current_roll=5,
            might_spent=2,
            might_available=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for Duel roll above 6.")


def test_apply_might_to_roll_rejects_negative_spend():
    try:
        apply_might_to_roll(
            current_roll=4,
            might_spent=-1,
            might_available=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative Might spend.")

def test_duel_might_strategy_values():
    assert DuelMightStrategy.NEVER.value == "never"
    assert (
        DuelMightStrategy.MINIMUM_TO_WIN.value
        == "minimum_to_win"
    )
    assert (
        DuelMightStrategy.MINIMUM_TO_AVOID_LOSS.value
        == "minimum_to_avoid_loss"
    )
    assert (
        DuelMightStrategy.MAXIMISE_ROLL.value
        == "maximise_roll"
    )

def test_never_strategy_spends_no_might():
    result = choose_might_spend(
        current_roll=4,
        might_available=3,
        strategy=DuelMightStrategy.NEVER,
    )

    assert result == 0


def test_maximise_roll_strategy_spends_to_reach_six():
    result = choose_might_spend(
        current_roll=4,
        might_available=3,
        strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result == 2


def test_maximise_roll_strategy_uses_all_available_when_needed():
    result = choose_might_spend(
        current_roll=3,
        might_available=2,
        strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result == 2


def test_maximise_roll_strategy_spends_nothing_on_six():
    result = choose_might_spend(
        current_roll=6,
        might_available=3,
        strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result == 0

def test_minimum_to_win_spends_required_might():
    result = choose_might_spend(
        current_roll=4,
        opponent_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert result == 2


def test_minimum_to_win_spends_nothing_when_already_winning():
    result = choose_might_spend(
        current_roll=6,
        opponent_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert result == 0


def test_minimum_to_win_spends_nothing_when_win_is_unreachable():
    result = choose_might_spend(
        current_roll=3,
        opponent_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert result == 0


def test_minimum_to_win_cannot_beat_six():
    result = choose_might_spend(
        current_roll=5,
        opponent_roll=6,
        might_available=3,
        strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert result == 0


def test_minimum_to_win_requires_opponent_roll():
    try:
        choose_might_spend(
            current_roll=4,
            might_available=2,
            strategy=DuelMightStrategy.MINIMUM_TO_WIN,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when opponent roll is missing."
        )

def test_minimum_to_avoid_loss_spends_to_tie():
    result = choose_might_spend(
        current_roll=4,
        opponent_roll=5,
        might_available=1,
        strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
    )

    assert result == 1


def test_minimum_to_avoid_loss_spends_nothing_when_already_tied():
    result = choose_might_spend(
        current_roll=5,
        opponent_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
    )

    assert result == 0


def test_minimum_to_avoid_loss_spends_nothing_when_already_winning():
    result = choose_might_spend(
        current_roll=6,
        opponent_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
    )

    assert result == 0


def test_minimum_to_avoid_loss_spends_nothing_when_tie_is_unreachable():
    result = choose_might_spend(
        current_roll=3,
        opponent_roll=6,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
    )

    assert result == 0


def test_minimum_to_avoid_loss_requires_opponent_roll():
    try:
        choose_might_spend(
            current_roll=4,
            might_available=2,
            strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when opponent roll is missing."
        )

def test_resolve_might_modified_roll_returns_final_roll_and_spend():
    final_roll, might_spent = resolve_might_modified_roll(
        current_roll=4,
        opponent_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert final_roll == 6
    assert might_spent == 2


def test_resolve_might_modified_roll_returns_no_change_when_not_spending():
    final_roll, might_spent = resolve_might_modified_roll(
        current_roll=5,
        might_available=2,
        strategy=DuelMightStrategy.NEVER,
    )

    assert final_roll == 5
    assert might_spent == 0


def test_resolve_might_modified_roll_can_tie_opponent():
    final_roll, might_spent = resolve_might_modified_roll(
        current_roll=4,
        opponent_roll=5,
        might_available=1,
        strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
    )

    assert final_roll == 5
    assert might_spent == 1

def test_resolve_duel_might_allows_defender_to_react():
    result = resolve_duel_might(
        attacker_roll=4,
        attacker_might_available=2,
        attacker_strategy=DuelMightStrategy.MINIMUM_TO_WIN,
        defender_roll=5,
        defender_might_available=1,
        defender_strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
    )

    assert result == DuelMightResolution(
        attacker_final_roll=6,
        defender_final_roll=6,
        attacker_might_spent=2,
        defender_might_spent=1,
    )


def test_resolve_duel_might_supports_no_spending():
    result = resolve_duel_might(
        attacker_roll=4,
        attacker_might_available=2,
        attacker_strategy=DuelMightStrategy.NEVER,
        defender_roll=5,
        defender_might_available=2,
        defender_strategy=DuelMightStrategy.NEVER,
    )

    assert result == DuelMightResolution(
        attacker_final_roll=4,
        defender_final_roll=5,
        attacker_might_spent=0,
        defender_might_spent=0,
    )


def test_resolve_duel_might_caps_both_sides_at_six():
    result = resolve_duel_might(
        attacker_roll=5,
        attacker_might_available=3,
        attacker_strategy=DuelMightStrategy.MAXIMISE_ROLL,
        defender_roll=5,
        defender_might_available=3,
        defender_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result == DuelMightResolution(
        attacker_final_roll=6,
        defender_final_roll=6,
        attacker_might_spent=1,
        defender_might_spent=1,
    )

def test_resolve_duel_might_gives_attacker_priority():
    result = resolve_duel_might(
        attacker_roll=4,
        attacker_might_available=1,
        attacker_strategy=DuelMightStrategy.MINIMUM_TO_AVOID_LOSS,
        defender_roll=5,
        defender_might_available=1,
        defender_strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert result == DuelMightResolution(
        attacker_final_roll=5,
        defender_final_roll=6,
        attacker_might_spent=1,
        defender_might_spent=1,
    )









