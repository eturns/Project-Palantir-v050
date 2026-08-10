from pathlib import Path

from model_platform import PlatformType
from model_platform_loader import load_platforms


def test_load_platforms():
    platforms = load_platforms()

    chariot = platforms[
        "PLATFORM_IRON_HILLS_CHARIOT"
    ]

    assert chariot.name == "Iron Hills Chariot"
    assert chariot.platform_type is (
        PlatformType.CHARIOT
    )


def test_load_platforms_returns_entities_indexed_by_id():
    platforms = load_platforms()

    chariot = platforms[
        "PLATFORM_IRON_HILLS_CHARIOT"
    ]

    assert chariot.id == (
        "PLATFORM_IRON_HILLS_CHARIOT"
    )


def test_load_platforms_rejects_duplicate_id(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate_platforms.csv"

    file_path.write_text(
        "id,name,platform_type\n"
        "PLATFORM_TEST,First Platform,chariot\n"
        "PLATFORM_TEST,Second Platform,vehicle\n",
        encoding="utf-8",
    )

    try:
        load_platforms(
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "Platform ID."
        )


def test_load_platforms_rejects_unknown_type(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_type.csv"

    file_path.write_text(
        "id,name,platform_type\n"
        "PLATFORM_TEST,Test Platform,unknown\n",
        encoding="utf-8",
    )

    try:
        load_platforms(
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "Platform type."
        )