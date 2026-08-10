from pathlib import Path

from mount_loader import load_mounts


def test_load_mounts():
    mounts = load_mounts()

    assert mounts["MOUNT_WAR_BOAR"].name == (
        "War Boar"
    )

    assert mounts[
        "MOUNT_IRON_HILLS_GOAT"
    ].name == "Iron Hills Goat"


def test_load_mounts_returns_entities_indexed_by_id():
    mounts = load_mounts()

    assert mounts["MOUNT_WAR_BOAR"].id == (
        "MOUNT_WAR_BOAR"
    )

    assert mounts[
        "MOUNT_IRON_HILLS_GOAT"
    ].id == "MOUNT_IRON_HILLS_GOAT"


def test_load_mounts_rejects_duplicate_id(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate_mounts.csv"

    file_path.write_text(
        "id,name\n"
        "MOUNT_TEST,First Mount\n"
        "MOUNT_TEST,Second Mount\n",
        encoding="utf-8",
    )

    try:
        load_mounts(
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "Mount ID."
        )