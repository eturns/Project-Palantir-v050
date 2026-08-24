from army_break_state import is_army_broken
from army_counted_model_sources import (
    calculate_counted_models,
)
from army_model_state import ArmyModelState
from army_model_state_transition import (
    apply_model_casualties,
)
from army_quarter_strength_state import (
    is_army_at_or_below_quarter_strength,
)
from unholy_resurrection_marker_state import (
    UnholyResurrectionMarkerState,
)


def test_army_transitions_from_healthy_to_broken():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=11,
    )

    assert is_army_broken(state) is False

    state = apply_model_casualties(
        state,
        casualties=6,
    )

    assert state.remaining_models == 5
    assert is_army_broken(state) is True


def test_army_transitions_from_broken_to_quarter_strength():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    assert is_army_broken(state) is True
    assert (
        is_army_at_or_below_quarter_strength(state)
        is False
    )

    state = apply_model_casualties(
        state,
        casualties=3,
    )

    assert state.remaining_models == 2
    assert (
        is_army_at_or_below_quarter_strength(state)
        is True
    )


def test_unholy_resurrection_marker_can_delay_broken_state():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    marker_state = UnholyResurrectionMarkerState(
        marker_count=1,
    )

    counted_models = calculate_counted_models(
        marker_state,
    )

    assert is_army_broken(
        state,
        counted_models=counted_models,
    ) is False


def test_unholy_resurrection_marker_can_delay_quarter_strength():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=2,
    )

    marker_state = UnholyResurrectionMarkerState(
        marker_count=1,
    )

    counted_models = calculate_counted_models(
        marker_state,
    )

    assert (
        is_army_at_or_below_quarter_strength(
            state,
            counted_models=counted_models,
        )
        is False
    )


def test_unholy_resurrection_marker_does_not_count_for_objectives():
    marker_state = UnholyResurrectionMarkerState(
        marker_count=3,
    )

    assert marker_state.counted_models == 3
    assert marker_state.objective_models == 0