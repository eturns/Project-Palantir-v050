from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from wargear import Wargear


def test_assignment_can_grant_wargear():
    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    assignment = ProfileOptionWargearAssignment(
        wargear=shield,
        action=WargearAssignmentAction.GRANT,
    )

    assert assignment.wargear is shield
    assert assignment.action == WargearAssignmentAction.GRANT


def test_assignment_can_remove_wargear():
    spear = Wargear(
        id="WG_SPEAR",
        name="Spear",
    )

    assignment = ProfileOptionWargearAssignment(
        wargear=spear,
        action=WargearAssignmentAction.REMOVE,
    )

    assert assignment.wargear is spear
    assert assignment.action == WargearAssignmentAction.REMOVE


def test_assignment_is_immutable():
    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    assignment = ProfileOptionWargearAssignment(
        wargear=shield,
        action=WargearAssignmentAction.GRANT,
    )

    try:
        assignment.action = WargearAssignmentAction.REMOVE
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected ProfileOptionWargearAssignment "
            "to be immutable."
        )


def test_assignment_reuses_existing_wargear_entity():
    mattock = Wargear(
        id="WG_MATTOCK",
        name="Mattock",
    )

    assignment = ProfileOptionWargearAssignment(
        wargear=mattock,
        action=WargearAssignmentAction.GRANT,
    )

    assert assignment.wargear is mattock