from mount import Mount
from profiles import Profile


def create_test_profile(
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


def test_profile_has_no_default_mount_by_default():
    profile = create_test_profile()

    assert profile.default_mount is None


def test_profile_can_have_default_mount():
    mount = Mount(
        id="MOUNT_TEST",
        name="Test Mount",
    )

    profile = create_test_profile(
        default_mount=mount,
    )

    assert profile.default_mount is mount