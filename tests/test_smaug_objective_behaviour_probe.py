from forced_action_constraint import (
    ForcedActionConstraint,
    ForcedActionTarget,
    ForcedActionType,
    filter_forced_action_targets,
)
from objective_control import resolve_objective_control
from objective_control_override import (
    ObjectiveControlOverride,
)
from victory_point_modifier import (
    VictoryPointModifier,
    apply_victory_point_modifier,
)

def test_objective_control_override_and_forced_charge_can_coexist():
    control_result = resolve_objective_control(
        first_army_presence=1,
        second_army_presence=20,
        first_army_override=(
            ObjectiveControlOverride.AUTOMATIC_CONTROL
        ),
        second_army_override=(
            ObjectiveControlOverride.NONE
        ),
    )

    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    targets = (
        ForcedActionTarget(
            id="OBJECTIVE_CARRIER",
            eligible=True,
        ),
        ForcedActionTarget(
            id="OTHER_MODEL",
            eligible=False,
        ),
    )

    charge_targets = filter_forced_action_targets(
        constraint=constraint,
        targets=targets,
        condition_met=True,
    )

    assert control_result == 1

    assert tuple(
        target.id
        for target in charge_targets
    ) == ("OBJECTIVE_CARRIER",)

def test_objective_control_forced_charge_and_victory_points_can_coexist():
    control_result = resolve_objective_control(
        first_army_presence=1,
        second_army_presence=20,
        first_army_override=(
            ObjectiveControlOverride.AUTOMATIC_CONTROL
        ),
        second_army_override=(
            ObjectiveControlOverride.NONE
        ),
    )

    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    targets = (
        ForcedActionTarget(
            id="GOLD_MARKER_CARRIER",
            eligible=True,
        ),
        ForcedActionTarget(
            id="OTHER_MODEL",
            eligible=False,
        ),
    )

    charge_targets = filter_forced_action_targets(
        constraint=constraint,
        targets=targets,
        condition_met=True,
    )

    modifier = VictoryPointModifier(
        amount=2,
        maximum_total=20,
    )

    victory_points = apply_victory_point_modifier(
        current_points=19,
        modifier=modifier,
        condition_met=True,
    )

    assert control_result == 1

    assert tuple(
        target.id
        for target in charge_targets
    ) == ("GOLD_MARKER_CARRIER",)

    assert victory_points == 20