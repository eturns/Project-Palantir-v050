from configured_profile import (
    ConfiguredProfile,
    create_configured_profile_from_external_options,
)
from profile_option import ProfileOption
from profiles import Profile
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from wargear import Wargear


def create_test_profile(
    profile_id: str = "IH_WR",
    points: int = 10,
) -> Profile:
    return Profile(
        id=profile_id,
        name="Iron Hills Warrior",
        points=points,
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


def test_configured_profile_without_options_uses_base_points():
    profile = create_test_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.points == 10


def test_configured_profile_adds_selected_option_points():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
    )
    profile.profile_options.append(shield_and_spear)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(shield_and_spear,),
    )

    assert configured_profile.points == 12


def test_configured_profile_adds_multiple_option_points():
    profile = create_test_profile(points=80)

    first_option = ProfileOption(
        id="FIRST_OPTION",
        name="First option",
        points=25,
    )

    second_option = ProfileOption(
        id="SECOND_OPTION",
        name="Second option",
        points=5,
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    assert configured_profile.points == 110


def test_configured_profile_allows_free_option():
    profile = create_test_profile(points=80)

    mattock_exchange = ProfileOption(
        id="IH_CAP_MATTOCK",
        name="Exchange shield and spear for Mattock",
        points=0,
        external_id="OPT0720",
    )

    profile.profile_options.append(mattock_exchange)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(mattock_exchange,),
    )

    assert configured_profile.points == 80


def test_configured_profile_preserves_canonical_profile():
    profile = create_test_profile()

    option = ProfileOption(
        id="IH_WR_CROSSBOW",
        name="Crossbow",
        points=2,
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.profile is profile
    assert profile.points == 10

def test_configured_profile_accepts_legal_selected_option():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    profile.profile_options.append(shield_and_spear)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(shield_and_spear,),
    )

    assert configured_profile.selected_options == (
        shield_and_spear,
    )


def test_configured_profile_rejects_illegal_selected_option():
    profile = create_test_profile()

    crossbow = ProfileOption(
        id="IH_WR_CROSSBOW",
        name="Crossbow",
        points=2,
    )

    try:
        ConfiguredProfile(
            profile=profile,
            selected_options=(crossbow,),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an option "
            "that is not legal for the Profile."
        )

def test_effective_wargear_uses_profile_default_wargear():
    profile = create_test_profile()

    heavy_armour = Wargear(
        id="WG_HEAVY_ARMOUR",
        name="Heavy armour",
    )

    hand_weapon = Wargear(
        id="WG_HAND_WEAPON",
        name="Hand weapon",
    )

    profile.default_wargear.extend(
        (
            heavy_armour,
            hand_weapon,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_wargear == (
        heavy_armour,
        hand_weapon,
    )


def test_effective_wargear_applies_granted_wargear():
    profile = create_test_profile()

    heavy_armour = Wargear(
        id="WG_HEAVY_ARMOUR",
        name="Heavy armour",
    )

    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    profile.default_wargear.append(heavy_armour)

    option = ProfileOption(
        id="IH_WR_SHIELD",
        name="Shield",
        points=1,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_wargear == (
        heavy_armour,
        shield,
    )


def test_effective_wargear_applies_removed_wargear():
    profile = create_test_profile()

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

    profile.default_wargear.extend(
        (
            shield,
            spear,
        )
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

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_wargear == (
        mattock,
    )


def test_effective_wargear_does_not_mutate_profile_defaults():
    profile = create_test_profile()

    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    option = ProfileOption(
        id="REMOVE_SHIELD",
        name="Remove shield",
        points=0,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.REMOVE,
            ),
        ),
    )

    profile.default_wargear.append(shield)
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_wargear == ()
    assert profile.default_wargear == [shield]

def test_configured_profile_rejects_duplicate_selected_option():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    profile.profile_options.append(shield_and_spear)

    try:
        ConfiguredProfile(
            profile=profile,
            selected_options=(
                shield_and_spear,
                shield_and_spear,
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when the same option "
            "is selected more than once."
        )


def test_configured_profile_accepts_distinct_selected_options():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_OPTION",
        name="First option",
        points=1,
    )

    second_option = ProfileOption(
        id="SECOND_OPTION",
        name="Second option",
        points=2,
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    assert configured_profile.selected_options == (
        first_option,
        second_option,
    )

def test_create_configured_profile_from_external_options():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
    )

    profile.profile_options.append(shield_and_spear)

    configured_profile = (
        create_configured_profile_from_external_options(
            profile=profile,
            external_option_ids=("OPT0723",),
            profile_options_by_external_id={
                "OPT0723": shield_and_spear,
            },
        )
    )

    assert configured_profile.profile is profile
    assert configured_profile.selected_options == (
        shield_and_spear,
    )
    assert configured_profile.points == 12


def test_external_option_configuration_rejects_unknown_id():
    profile = create_test_profile()

    try:
        create_configured_profile_from_external_options(
            profile=profile,
            external_option_ids=("OPT9999",),
            profile_options_by_external_id={},
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "external Profile Option ID."
        )


def test_external_option_configuration_rejects_option_for_wrong_profile():
    profile = create_test_profile()

    other_option = ProfileOption(
        id="OTHER_PROFILE_OPTION",
        name="Other Profile option",
        points=2,
        external_id="OPT0001",
    )

    try:
        create_configured_profile_from_external_options(
            profile=profile,
            external_option_ids=("OPT0001",),
            profile_options_by_external_id={
                "OPT0001": other_option,
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when the external option "
            "is not legal for the Profile."
        )