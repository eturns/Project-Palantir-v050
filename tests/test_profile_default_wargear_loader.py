from pathlib import Path

from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from profiles import Profile
from wargear_loader import load_wargear
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)

def create_test_profile(
    profile_id: str = "IH_WR",
) -> Profile:
    return Profile(
        id=profile_id,
        name="Iron Hills Warrior",
        points=10,
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


def test_load_profile_default_wargear():
    profile = create_test_profile()
    wargear = load_wargear()

    profiles = {
        loaded_profile.id: loaded_profile
        for loaded_profile
        in load_iron_hills_test_profiles()
    }
    profiles["IH_WR"] = profile

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    assert tuple(
        item.id
        for item in profile.default_wargear
    ) == (
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
    )


def test_load_profile_default_wargear_uses_master_entities():
    profile = create_test_profile()
    wargear = load_wargear()

    profiles = {
        loaded_profile.id: loaded_profile
        for loaded_profile
        in load_iron_hills_test_profiles()
    }
    profiles["IH_WR"] = profile

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    assert profile.default_wargear[0] is (
        wargear["WG_HEAVY_ARMOUR"]
    )

    assert profile.default_wargear[1] is (
        wargear["WG_HAND_WEAPON"]
    )


def test_load_profile_default_wargear_rejects_unknown_profile(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_profile.csv"

    file_path.write_text(
        "profile_id,wargear_id\n"
        "UNKNOWN,WG_SHIELD\n",
        encoding="utf-8",
    )

    try:
        load_profile_default_wargear(
            profiles={"IH_WR": create_test_profile()},
            wargear=load_wargear(),
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Profile ID."
        )


def test_load_profile_default_wargear_rejects_unknown_wargear(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_wargear.csv"

    file_path.write_text(
        "profile_id,wargear_id\n"
        "IH_WR,UNKNOWN\n",
        encoding="utf-8",
    )

    try:
        load_profile_default_wargear(
            profiles={"IH_WR": create_test_profile()},
            wargear={},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Wargear ID."
        )


def test_load_profile_default_wargear_rejects_duplicate_assignment(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate_assignment.csv"

    file_path.write_text(
        "profile_id,wargear_id\n"
        "IH_WR,WG_SHIELD\n"
        "IH_WR,WG_SHIELD\n",
        encoding="utf-8",
    )

    profile = create_test_profile()
    wargear = load_wargear()

    try:
        load_profile_default_wargear(
            profiles={"IH_WR": profile},
            wargear=wargear,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "default Wargear assignment."
        )