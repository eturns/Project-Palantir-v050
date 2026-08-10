from pathlib import Path

from profile_option_loader import (
    build_profile_options_by_external_id,
    load_profile_options,
)
from profile_option import ProfileOption
from profiles import Profile
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
def create_iron_hills_profiles(
    warrior: Profile | None = None,
) -> dict[str, Profile]:
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }

    if warrior is not None:
        profiles["IH_WR"] = warrior

    return profiles

def test_load_profile_options_returns_options_by_id():
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    assert options["IH_WR_SHIELD_SPEAR"].name == (
        "Shield and spear"
    )
    assert options["IH_WR_SHIELD_SPEAR"].points == 2
    assert options["IH_WR_SHIELD_SPEAR"].external_id == "OPT0723"


def test_load_profile_options_attaches_options_to_profile():
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    expected_warrior_options = [
        option
        for option in options.values()
        if option in profile.profile_options
    ]

    assert profile.profile_options == expected_warrior_options


def test_load_profile_options_loads_iron_hills_warrior_options():
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    assert len(profile.profile_options) == 5


def test_load_profile_options_rejects_unknown_profile(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_profile_options.csv"

    file_path.write_text(
        "id,profile_id,name,points,external_id\n"
        "UNKNOWN_OPTION,UNKNOWN,Shield,1,OPT0001\n",
        encoding="utf-8",
    )

    try:
        load_profile_options(
            profiles={"IH_WR": create_test_profile()},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Profile ID."
        )


def test_load_profile_options_rejects_duplicate_option_ids(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate_options.csv"

    file_path.write_text(
        "id,profile_id,name,points,external_id\n"
        "DUPLICATE,IH_WR,Shield,1,OPT0001\n"
        "DUPLICATE,IH_WR,Spear,1,OPT0002\n",
        encoding="utf-8",
    )

    try:
        load_profile_options(
            profiles={"IH_WR": create_test_profile()},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate option ID."
        )


def test_load_profile_options_rejects_duplicate_external_ids(
    tmp_path: Path,
):
    file_path = tmp_path / "duplicate_external_options.csv"

    file_path.write_text(
        "id,profile_id,name,points,external_id\n"
        "FIRST,IH_WR,Shield,1,OPT0001\n"
        "SECOND,IH_WR,Spear,1,OPT0001\n",
        encoding="utf-8",
    )

    try:
        load_profile_options(
            profiles={"IH_WR": create_test_profile()},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate external option ID."
        )

def test_build_profile_options_by_external_id():
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(options)
    )

    assert options_by_external_id["OPT0723"] is (
        options["IH_WR_SHIELD_SPEAR"]
    )

    assert options_by_external_id["OPT0724"] is (
        options["IH_WR_CROSSBOW"]
    )


def test_external_option_lookup_omits_options_without_external_id():
    option_with_external_id = ProfileOption(
        id="WITH_EXTERNAL",
        name="With external ID",
        points=1,
        external_id="OPT0001",
    )

    option_without_external_id = ProfileOption(
        id="WITHOUT_EXTERNAL",
        name="Without external ID",
        points=1,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            {
                option_with_external_id.id:
                    option_with_external_id,
                option_without_external_id.id:
                    option_without_external_id,
            }
        )
    )

    assert options_by_external_id == {
        "OPT0001": option_with_external_id,
    }


def test_external_option_lookup_rejects_duplicate_external_ids():
    first_option = ProfileOption(
        id="FIRST",
        name="First option",
        points=1,
        external_id="OPT0001",
    )

    second_option = ProfileOption(
        id="SECOND",
        name="Second option",
        points=2,
        external_id="OPT0001",
    )

    try:
        build_profile_options_by_external_id(
            {
                first_option.id: first_option,
                second_option.id: second_option,
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "external Profile Option ID."
        )

def test_loads_remaining_iron_hills_options():
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    war_boar = options["IH_DAIN_WAR_BOAR"]
    assert war_boar.points == 25
    assert war_boar.external_id == "OPT0718"
    assert war_boar in profiles["IH_DAIN"].profile_options

    chariot = options["IH_CAP_CHARIOT"]
    assert chariot.points == 170
    assert chariot.external_id == "OPT0719"
    assert chariot in profiles["IH_CAP"].profile_options

    captain_mattock = options["IH_CAP_MATTOCK"]
    assert captain_mattock.points == 0
    assert captain_mattock.external_id == "OPT0720"
    assert captain_mattock in (
        profiles["IH_CAP"].profile_options
    )

    goat_rider_mattock = options["IH_GR_MATTOCK"]
    assert goat_rider_mattock.points == 0
    assert goat_rider_mattock.external_id == "OPT0726"
    assert goat_rider_mattock in (
        profiles["IH_GR"].profile_options
    )