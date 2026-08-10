from pathlib import Path

from profile_option_loader import load_profile_options
from profile_option_wargear_assignment import (
    WargearAssignmentAction,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from profiles import Profile
from wargear_loader import load_wargear
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)


def create_test_profile() -> Profile:
    return Profile(
        id="IH_WR",
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
def test_load_option_wargear_assignments():
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    wargear = load_wargear()

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    option = options["IH_WR_SHIELD_SPEAR"]

    assert len(option.wargear_assignments) == 2

    assert option.wargear_assignments[0].wargear.id == (
        "WG_SHIELD"
    )

    assert option.wargear_assignments[0].action == (
        WargearAssignmentAction.GRANT
    )

    assert option.wargear_assignments[1].wargear.id == (
        "WG_SPEAR"
    )

    assert option.wargear_assignments[1].action == (
        WargearAssignmentAction.GRANT
    )


def test_load_option_wargear_assignments_supports_packages():
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    wargear = load_wargear()

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    option = options["IH_WR_BANNER_SHIELD"]

    assert tuple(
        assignment.wargear.id
        for assignment in option.wargear_assignments
    ) == (
        "WG_BANNER",
        "WG_SHIELD",
    )


def test_load_option_wargear_rejects_unknown_option(
    tmp_path: Path,
):
    file_path = tmp_path / "unknown_option.csv"

    file_path.write_text(
        "option_id,wargear_id,action\n"
        "UNKNOWN,WG_SHIELD,grant\n",
        encoding="utf-8",
    )

    try:
        load_profile_option_wargear_assignments(
            profile_options={},
            wargear=load_wargear(),
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Profile Option."
        )


def test_load_option_wargear_rejects_unknown_wargear(
    tmp_path: Path,
):
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    file_path = tmp_path / "unknown_wargear.csv"

    file_path.write_text(
        "option_id,wargear_id,action\n"
        "IH_WR_SHIELD_SPEAR,UNKNOWN,grant\n",
        encoding="utf-8",
    )

    try:
        load_profile_option_wargear_assignments(
            profile_options=options,
            wargear={},
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown Wargear."
        )


def test_load_option_wargear_rejects_unknown_action(
    tmp_path: Path,
):
    profile = create_test_profile()

    profiles = create_iron_hills_profiles(
        warrior=profile,
    )

    options = load_profile_options(
        profiles=profiles,
    )

    wargear = load_wargear()

    file_path = tmp_path / "unknown_action.csv"

    file_path.write_text(
        "option_id,wargear_id,action\n"
        "IH_WR_SHIELD_SPEAR,WG_SHIELD,replace\n",
        encoding="utf-8",
    )

    try:
        load_profile_option_wargear_assignments(
            profile_options=options,
            wargear=wargear,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown assignment action."
        )