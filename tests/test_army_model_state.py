import pytest

from army_model_state import ArmyModelState


def test_army_model_state_stores_starting_and_remaining_models():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=11,
    )

    assert state.starting_models == 11
    assert state.remaining_models == 11


def test_army_model_state_rejects_negative_starting_models():
    with pytest.raises(
        ValueError,
        match="Starting model count cannot be negative.",
    ):
        ArmyModelState(
            starting_models=-1,
            remaining_models=0,
        )


def test_army_model_state_rejects_negative_remaining_models():
    with pytest.raises(
        ValueError,
        match="Remaining model count cannot be negative.",
    ):
        ArmyModelState(
            starting_models=11,
            remaining_models=-1,
        )


def test_army_model_state_rejects_more_remaining_than_started():
    with pytest.raises(
        ValueError,
        match="Remaining model count cannot exceed starting model count.",
    ):
        ArmyModelState(
            starting_models=11,
            remaining_models=12,
        )