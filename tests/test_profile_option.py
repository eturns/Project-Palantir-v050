from profile_option import ProfileOption
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from wargear import Wargear
from mount import Mount
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from model_platform import Platform, PlatformType
from profile_option_platform_assignment import (
    ProfileOptionPlatformAssignment,
)

def test_profile_option_stores_identity_and_points():
    option = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    assert option.id == "IH_WR_SHIELD_SPEAR"
    assert option.name == "Shield and spear"
    assert option.points == 2


def test_profile_option_external_id_defaults_to_none():
    option = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    assert option.external_id is None


def test_profile_option_can_store_external_id():
    option = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
    )

    assert option.external_id == "OPT0723"


def test_profile_option_allows_free_option():
    option = ProfileOption(
        id="IH_CAP_MATTOCK",
        name="Exchange shield and spear for Mattock",
        points=0,
        external_id="OPT0720",
    )

    assert option.points == 0


def test_profile_option_rejects_negative_points():
    try:
        ProfileOption(
            id="INVALID",
            name="Invalid option",
            points=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for negative option points."
        )


def test_profile_option_rejects_empty_id():
    try:
        ProfileOption(
            id="",
            name="Shield and spear",
            points=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty profile option ID."
        )


def test_profile_option_rejects_empty_name():
    try:
        ProfileOption(
            id="IH_WR_SHIELD_SPEAR",
            name="",
            points=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty profile option name."
        )


def test_profile_option_rejects_blank_external_id():
    try:
        ProfileOption(
            id="IH_WR_SHIELD_SPEAR",
            name="Shield and spear",
            points=2,
            external_id="   ",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for blank external option ID."
        )

def test_profile_option_wargear_assignments_default_to_empty():
    option = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    assert option.wargear_assignments == ()


def test_profile_option_can_store_multiple_wargear_assignments():
    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    spear = Wargear(
        id="WG_SPEAR",
        name="Spear",
    )

    shield_assignment = ProfileOptionWargearAssignment(
        wargear=shield,
        action=WargearAssignmentAction.GRANT,
    )

    spear_assignment = ProfileOptionWargearAssignment(
        wargear=spear,
        action=WargearAssignmentAction.GRANT,
    )

    option = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
        wargear_assignments=(
            shield_assignment,
            spear_assignment,
        ),
    )

    assert option.wargear_assignments == (
        shield_assignment,
        spear_assignment,
    )


def test_profile_option_can_store_grants_and_removals():
    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    spear = Wargear(
        id="WG_SPEAR",
        name="Spear",
    )

    mattock = Wargear(
        id="WG_MATTOCK",
        name="Mattock",
    )

    option = ProfileOption(
        id="IH_CAP_MATTOCK",
        name="Exchange shield and spear for Mattock",
        points=0,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.REMOVE,
            ),
            ProfileOptionWargearAssignment(
                wargear=spear,
                action=WargearAssignmentAction.REMOVE,
            ),
            ProfileOptionWargearAssignment(
                wargear=mattock,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )

    assert len(option.wargear_assignments) == 3

    assert option.wargear_assignments[0].action == (
        WargearAssignmentAction.REMOVE
    )

    assert option.wargear_assignments[1].action == (
        WargearAssignmentAction.REMOVE
    )

    assert option.wargear_assignments[2].action == (
        WargearAssignmentAction.GRANT
    )

def test_profile_option_defaults_to_no_mount_assignments():
    option = ProfileOption(
        id="IH_DAIN_WAR_BOAR",
        name="War Boar",
        points=25,
        external_id="OPT0718",
    )

    assert option.mount_assignments == ()


def test_profile_option_stores_mount_assignment():
    war_boar = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
    )

    assignment = ProfileOptionMountAssignment(
        mount=war_boar,
    )

    option = ProfileOption(
        id="IH_DAIN_WAR_BOAR",
        name="War Boar",
        points=25,
        external_id="OPT0718",
        mount_assignments=(
            assignment,
        ),
    )

    assert option.mount_assignments == (
        assignment,
    )

    assert option.mount_assignments[0].mount is (
        war_boar
    )

def test_profile_option_defaults_to_no_platform_assignments():
    option = ProfileOption(
        id="IH_CAP_CHARIOT",
        name="Iron Hills Chariot",
        points=170,
        external_id="OPT0719",
    )

    assert option.platform_assignments == ()


def test_profile_option_stores_platform_assignment():
    chariot = Platform(
        id="PLATFORM_IRON_HILLS_CHARIOT",
        name="Iron Hills Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    assignment = ProfileOptionPlatformAssignment(
        platform=chariot,
    )

    option = ProfileOption(
        id="IH_CAP_CHARIOT",
        name="Iron Hills Chariot",
        points=170,
        external_id="OPT0719",
        platform_assignments=(
            assignment,
        ),
    )

    assert option.platform_assignments == (
        assignment,
    )

    assert option.platform_assignments[0].platform is (
        chariot
    )