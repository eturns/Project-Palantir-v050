from pathlib import Path

from wargear_loader import load_wargear
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)

def test_load_wargear_returns_entities_by_id():
    wargear = load_wargear()

    assert wargear["WG_SHIELD"].name == "Shield"
    assert wargear["WG_SPEAR"].name == "Spear"
    assert wargear["WG_MATTOCK"].name == "Mattock"


def test_load_wargear_loads_expected_iron_hills_foundation():
    wargear = load_wargear()

    assert len(wargear) == 11


def test_load_wargear_rejects_duplicate_ids(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate_wargear.csv"

    file_path.write_text(
        "id,name\n"
        "WG_SHIELD,Shield\n"
        "WG_SHIELD,Duplicate Shield\n",
        encoding="utf-8",
    )

    try:
        load_wargear(str(file_path))
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate Wargear ID."
        )

def test_loads_iron_hills_default_wargear():
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }
    wargear = load_wargear()

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    assert {
        item.id
        for item in profiles["IH_DAIN"].default_wargear
    } == {
        "WG_HEAVY_DWARF_ARMOUR",
        "WG_TWO_HANDED_WEAPON",
    }

    assert {
        item.id
        for item in profiles["IH_CAP"].default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_SHIELD",
        "WG_SPEAR",
        "WG_HAND_WEAPON",
    }

    assert {
        item.id
        for item in profiles["IH_GR"].default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_WAR_SPEAR",
        "WG_HAND_WEAPON",
    }

    assert {
        item.id
        for item in profiles["IH_CHARIOT"].default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_RAPID_FIRE_BOLT_THROWER",
    }