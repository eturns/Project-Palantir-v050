import pytest

from forced_action_constraint import (
    ForcedActionConstraint,
    ForcedActionTarget,
    ForcedActionType,
    filter_forced_action_targets,
)

def test_forced_action_constraint_requires_charge_of_eligible_target():
    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    assert constraint.action_type is ForcedActionType.CHARGE
    assert constraint.require_if_possible is True


def test_forced_action_constraint_requires_valid_action_type():
    with pytest.raises(TypeError):
        ForcedActionConstraint(
            action_type="charge",
            require_if_possible=True,
        )


def test_forced_action_constraint_requires_boolean_require_if_possible():
    with pytest.raises(TypeError):
        ForcedActionConstraint(
            action_type=ForcedActionType.CHARGE,
            require_if_possible="yes",
        )

def test_forced_charge_filters_to_eligible_targets():
    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    targets = (
        ForcedActionTarget(
            id="A",
            eligible=True,
        ),
        ForcedActionTarget(
            id="B",
            eligible=False,
        ),
        ForcedActionTarget(
            id="C",
            eligible=True,
        ),
    )

    result = filter_forced_action_targets(
        constraint=constraint,
        targets=targets,
    )

    assert tuple(
        target.id
        for target in result
    ) == (
        "A",
        "C",
    )


def test_forced_charge_returns_no_targets_when_none_are_eligible():
    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    targets = (
        ForcedActionTarget(
            id="A",
            eligible=False,
        ),
        ForcedActionTarget(
            id="B",
            eligible=False,
        ),
    )

    result = filter_forced_action_targets(
        constraint=constraint,
        targets=targets,
    )

    assert result == ()

def test_forced_action_constraint_does_not_filter_when_condition_is_not_met():
    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    targets = (
        ForcedActionTarget(
            id="A",
            eligible=True,
        ),
        ForcedActionTarget(
            id="B",
            eligible=False,
        ),
    )

    result = filter_forced_action_targets(
        constraint=constraint,
        targets=targets,
        condition_met=False,
    )

    assert result == targets


def test_forced_action_constraint_filters_when_condition_is_met():
    constraint = ForcedActionConstraint(
        action_type=ForcedActionType.CHARGE,
        require_if_possible=True,
    )

    targets = (
        ForcedActionTarget(
            id="A",
            eligible=True,
        ),
        ForcedActionTarget(
            id="B",
            eligible=False,
        ),
    )

    result = filter_forced_action_targets(
        constraint=constraint,
        targets=targets,
        condition_met=True,
    )

    assert tuple(
        target.id
        for target in result
    ) == ("A",)