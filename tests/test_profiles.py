from profile_option import ProfileOption
from profiles import Profile
from wargear import Wargear


def create_test_profile(profile_id: str) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id.replace("_", " ").title(),
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


def test_profile_options_default_to_empty():
    profile = create_test_profile("TEST_PROFILE")

    assert profile.profile_options == []


def test_profile_can_store_legal_profile_options():
    profile = create_test_profile("IRON_HILLS_WARRIOR")

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
    )

    crossbow = ProfileOption(
        id="IH_WR_CROSSBOW",
        name="Crossbow",
        points=2,
        external_id="OPT0724",
    )

    profile.profile_options.extend(
        (
            shield_and_spear,
            crossbow,
        )
    )

    assert profile.profile_options == [
        shield_and_spear,
        crossbow,
    ]


def test_profile_options_are_owned_independently_per_profile():
    first_profile = create_test_profile("FIRST_PROFILE")
    second_profile = create_test_profile("SECOND_PROFILE")

    option = ProfileOption(
        id="FIRST_OPTION",
        name="First option",
        points=1,
    )

    first_profile.profile_options.append(option)

    assert first_profile.profile_options == [option]
    assert second_profile.profile_options == []

def test_profile_default_wargear_defaults_to_empty():
    profile = create_test_profile("TEST_PROFILE")

    assert profile.default_wargear == []


def test_profile_can_store_default_wargear():
    profile = create_test_profile("IRON_HILLS_WARRIOR")

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

    assert profile.default_wargear == [
        heavy_armour,
        hand_weapon,
    ]


def test_default_wargear_is_owned_independently_per_profile():
    first_profile = create_test_profile("FIRST_PROFILE")
    second_profile = create_test_profile("SECOND_PROFILE")

    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    first_profile.default_wargear.append(shield)

    assert first_profile.default_wargear == [shield]
    assert second_profile.default_wargear == []

def test_profile_stores_base_size_mm():
    profile = Profile(
        id="TEST_BASE",
        name="Test Base",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        base_size_mm=25,
    )

    assert profile.base_size_mm == 25