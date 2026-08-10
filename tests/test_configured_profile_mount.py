from configured_profile import ConfiguredProfile
from mount import Mount
from profile_option import ProfileOption
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from profiles import Profile


def create_profile(
    default_mount: Mount | None = None,
) -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        default_mount=default_mount,
    )


def test_effective_mount_is_none_when_unmounted():
    configured_profile = ConfiguredProfile(
        profile=create_profile(),
    )

    assert configured_profile.effective_mount is None


def test_effective_mount_uses_profile_default_mount():
    mount = Mount(
        id="MOUNT_GOAT",
        name="War Goat",
    )

    configured_profile = ConfiguredProfile(
        profile=create_profile(
            default_mount=mount,
        ),
    )

    assert configured_profile.effective_mount is mount


def test_effective_mount_uses_selected_option_mount():
    mount = Mount(
        id="MOUNT_BOAR",
        name="War Boar",
    )

    option = ProfileOption(
        id="OPTION_BOAR",
        name="War Boar",
        points=25,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=mount,
            ),
        ),
    )

    profile = create_profile()
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_mount is mount


def test_option_mount_overrides_profile_default_mount():
    default_mount = Mount(
        id="MOUNT_GOAT",
        name="War Goat",
    )
    option_mount = Mount(
        id="MOUNT_BOAR",
        name="War Boar",
    )

    option = ProfileOption(
        id="OPTION_BOAR",
        name="War Boar",
        points=25,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=option_mount,
            ),
        ),
    )

    profile = create_profile(
        default_mount=default_mount,
    )
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_mount is (
        option_mount
    )


def test_rejects_multiple_option_mounts():
    first_mount = Mount(
        id="MOUNT_FIRST",
        name="First Mount",
    )
    second_mount = Mount(
        id="MOUNT_SECOND",
        name="Second Mount",
    )

    first_option = ProfileOption(
        id="OPTION_FIRST",
        name="First Mount",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=first_mount,
            ),
        ),
    )
    second_option = ProfileOption(
        id="OPTION_SECOND",
        name="Second Mount",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=second_mount,
            ),
        ),
    )

    profile = create_profile()
    profile.profile_options.extend(
        [
            first_option,
            second_option,
        ]
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_mount
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple Mounts."
        )