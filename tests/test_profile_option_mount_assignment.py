from mount import Mount
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)


def test_profile_option_mount_assignment_stores_mount():
    mount = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
    )

    assignment = ProfileOptionMountAssignment(
        mount=mount,
    )

    assert assignment.mount is mount


def test_profile_option_mount_assignment_is_immutable():
    war_boar = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
    )

    horse = Mount(
        id="MOUNT_HORSE",
        name="Horse",
    )

    assignment = ProfileOptionMountAssignment(
        mount=war_boar,
    )

    try:
        assignment.mount = horse
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected ProfileOptionMountAssignment "
            "to be immutable."
        )