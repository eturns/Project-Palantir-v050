from pathlib import Path

from model_platform_loader import load_platforms
from profile_option import ProfileOption
from profile_option_platform_loader import (
    load_profile_option_platform_assignments,
)


def create_chariot_option() -> ProfileOption:
    return ProfileOption(
        id="IH_CAP_CHARIOT",
        name="Iron Hills Chariot",
        points=170,
        external_id="OPT0719",
    )


def test_load_profile_option_platform_assignment():
    option = create_chariot_option()
    options = {
        option.id: option,
    }

    platforms = load_platforms()

    load_profile_option_platform_assignments(
        profile_options=options,
        platforms=platforms,
    )

    assert len(option.platform_assignments) == 1

    assert option.platform_assignments[0].platform is (
        platforms["PLATFORM_IRON_HILLS_CHARIOT"]
    )


def test_platform_assignment_uses_master_platform_entity():
    option = create_chariot_option()
    platforms = load_platforms()

    load_profile_option_platform_assignments(
        profile_options={
            option.id: option,
        },
        platforms=platforms,
    )

    assert option.platform_assignments[0].platform.id == (
        "PLATFORM_IRON_HILLS_CHARIOT"
    )


def test_platform_assignment_rejects_unknown_option(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_option.csv"

    file_path.write_text(
        "option_id,platform_id\n"
        "UNKNOWN,PLATFORM_IRON_HILLS_CHARIOT\n",
        encoding="utf-8",
    )

    try:
        load_profile_option_platform_assignments(
            profile_options={},
            platforms=load_platforms(),
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "Profile Option ID."
        )


def test_platform_assignment_rejects_unknown_platform(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_platform.csv"

    file_path.write_text(
        "option_id,platform_id\n"
        "IH_CAP_CHARIOT,UNKNOWN\n",
        encoding="utf-8",
    )

    option = create_chariot_option()

    try:
        load_profile_option_platform_assignments(
            profile_options={
                option.id: option,
            },
            platforms={},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Platform ID."
        )