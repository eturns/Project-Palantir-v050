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
    "id,name,base_size_mm\n"
    "MOUNT_TEST,First Mount,40\n"
    "MOUNT_TEST,Second Mount,40\n",
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

def test_load_mounts_loads_base_size():
    mounts = load_mounts()

    assert mounts["MOUNT_WAR_BOAR"].base_size_mm == 40
    assert mounts["MOUNT_IRON_HILLS_GOAT"].base_size_mm == 40

def test_load_mounts_reads_base_size_from_csv(tmp_path):
    file_path = tmp_path / "mounts.csv"

    file_path.write_text(
        "id,name,base_size_mm\n"
        "MOUNT_TEST,Test Mount,50\n",
        encoding="utf-8",
    )

    mounts = load_mounts(
        file_path=str(file_path),
    )

    assert mounts["MOUNT_TEST"].base_size_mm == 50