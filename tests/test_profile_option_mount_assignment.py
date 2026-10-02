from mount import Mount
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)


def test_profile_option_mount_assignment_stores_mount():
    mount = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
        movement=8,
        fight=4,
        shooting="6+",
        strength=4,
        defence=6,
        attacks=0,
        wounds=2,
        courage="7+",
        intelligence="7+",
        base_size_mm=40,
    )

    assignment = ProfileOptionMountAssignment(
        mount=mount,
    )

    assert assignment.mount is mount


def test_profile_option_mount_assignment_is_immutable():
    war_boar = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
        movement=8,
        fight=4,
        shooting="6+",
        strength=4,
        defence=6,
        attacks=0,
        wounds=2,
        courage="7+",
        intelligence="7+",
        base_size_mm=40,
    )

    horse = Mount(
        id="MOUNT_HORSE",
        name="Horse",
        movement=10,
        fight=2,
        shooting="6+",
        strength=3,
        defence=4,
        attacks=0,
        wounds=1,
        courage="7+",
        intelligence="7+",
        base_size_mm=40,
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