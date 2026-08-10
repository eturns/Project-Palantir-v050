import pytest

from battle_length_assumption import (
    BattleEndType,
    BattleHorizon,
    BattleLengthAssumption,
    battle_length_assumption_for_horizon,
)


def test_battle_length_assumption_stores_horizon():
    assumption = BattleLengthAssumption(
        assumed_turns=8,
        end_type=(
            BattleEndType.ARMY_AT_QUARTER_STRENGTH
        ),
    )

    assert assumption.assumed_turns == 8
    assert (
        assumption.end_type
        == BattleEndType.ARMY_AT_QUARTER_STRENGTH
    )


def test_battle_length_assumption_supports_random_end_context():
    assumption = BattleLengthAssumption(
        assumed_turns=7,
        end_type=BattleEndType.BROKEN_RANDOM_END,
    )

    assert (
        assumption.end_type
        == BattleEndType.BROKEN_RANDOM_END
    )


def test_battle_length_assumption_rejects_zero_turns():
    with pytest.raises(
        ValueError,
        match=(
            "Assumed battle length must be "
            "at least one turn."
        ),
    ):
        BattleLengthAssumption(
            assumed_turns=0,
            end_type=BattleEndType.FIXED_TURNS,
        )

def test_short_battle_horizon_is_six_turns():
    assumption = battle_length_assumption_for_horizon(
        horizon=BattleHorizon.SHORT,
        end_type=BattleEndType.BROKEN_RANDOM_END,
    )

    assert assumption.assumed_turns == 6


def test_medium_battle_horizon_is_eight_turns():
    assumption = battle_length_assumption_for_horizon(
        horizon=BattleHorizon.MEDIUM,
        end_type=BattleEndType.ARMY_AT_QUARTER_STRENGTH,
    )

    assert assumption.assumed_turns == 8


def test_long_battle_horizon_is_ten_turns():
    assumption = battle_length_assumption_for_horizon(
        horizon=BattleHorizon.LONG,
        end_type=BattleEndType.OBJECTIVE_COMPLETION,
    )

    assert assumption.assumed_turns == 10