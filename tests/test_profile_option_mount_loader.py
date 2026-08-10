from pathlib import Path

from mount_loader import load_mounts
from profile_option import ProfileOption
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)


def create_war_boar_option() -> ProfileOption:
    return ProfileOption(
        id="IH_DAIN_WAR_BOAR",
        name="War Boar",
        points=25,
        external_id="OPT0718",
    )


def test_load_profile_option_mount_assignment():
    option = create_war_boar_option()
    options = {
        option.id: option,
    }

    mounts = load_mounts()

    load_profile_option_mount_assignments(
        profile_options=options,
        mounts=mounts,
    )

    assert len(option.mount_assignments) == 1

    assert option.mount_assignments[0].mount is (
        mounts["MOUNT_WAR_BOAR"]
    )


def test_mount_assignment_uses_master_mount_entity():
    option = create_war_boar_option()
    mounts = load_mounts()

    load_profile_option_mount_assignments(
        profile_options={
            option.id: option,
        },
        mounts=mounts,
    )

    assert option.mount_assignments[0].mount.id == (
        "MOUNT_WAR_BOAR"
    )


def test_mount_assignment_rejects_unknown_option(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_option.csv"

    file_path.write_text(
        "option_id,mount_id\n"
        "UNKNOWN,MOUNT_WAR_BOAR\n",
        encoding="utf-8",
    )

    try:
        load_profile_option_mount_assignments(
            profile_options={},
            mounts=load_mounts(),
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "Profile Option ID."
        )


def test_mount_assignment_rejects_unknown_mount(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_mount.csv"

    file_path.write_text(
        "option_id,mount_id\n"
        "IH_DAIN_WAR_BOAR,UNKNOWN\n",
        encoding="utf-8",
    )

    option = create_war_boar_option()

    try:
        load_profile_option_mount_assignments(
            profile_options={
                option.id: option,
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