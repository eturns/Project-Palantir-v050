from pathlib import Path

from mount_loader import load_mounts
from profile_default_mount_loader import (
    load_profile_default_mounts,
)
from profiles import Profile


def create_profile() -> Profile:
    return Profile(
        id="IH_GR",
        name="Iron Hills Goat Rider",
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
    )


def test_load_profile_default_mount():
    profile = create_profile()
    profiles = {
        profile.id: profile,
    }
    mounts = load_mounts()

    load_profile_default_mounts(
        profiles=profiles,
        mounts=mounts,
    )

    assert profile.default_mount is (
        mounts["MOUNT_IRON_HILLS_GOAT"]
    )


def test_default_mount_uses_master_mount_entity():
    profile = create_profile()
    mounts = load_mounts()

    load_profile_default_mounts(
        profiles={
            profile.id: profile,
        },
        mounts=mounts,
    )

    assert profile.default_mount.id == (
        "MOUNT_IRON_HILLS_GOAT"
    )


def test_default_mount_rejects_unknown_profile(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_profile.csv"

    file_path.write_text(
        "profile_id,mount_id\n"
        "UNKNOWN,MOUNT_IRON_HILLS_GOAT\n",
        encoding="utf-8",
    )

    try:
        load_profile_default_mounts(
            profiles={},
            mounts=load_mounts(),
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "Profile ID."
        )


def test_default_mount_rejects_unknown_mount(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_mount.csv"

    file_path.write_text(
        "profile_id,mount_id\n"
        "IH_GR,UNKNOWN\n",
        encoding="utf-8",
    )

    profile = create_profile()

    try:
        load_profile_default_mounts(
            profiles={
                profile.id: profile,
            },
            mounts={},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Mount ID."
        )


def test_default_mount_rejects_duplicate_profile(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate.csv"

    file_path.write_text(
        "profile_id,mount_id\n"
        "IH_GR,MOUNT_IRON_HILLS_GOAT\n"
        "IH_GR,MOUNT_IRON_HILLS_GOAT\n",
        encoding="utf-8",
    )

    profile = create_profile()

    try:
        load_profile_default_mounts(
            profiles={
                profile.id: profile,
            },
            mounts=load_mounts(),
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "default Mount assignment."
        )