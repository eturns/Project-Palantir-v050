from configured_profile import ConfiguredProfile
from profile_option import ProfileOption
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from profiles import Profile
from ranged_weapon_profile import (
    RANGED_WEAPON_PROFILES,
    RangedWeaponProfile,
)
from ranged_weapon_resolver import resolve_ranged_weapon
from wargear import Wargear
import pytest

def create_test_warrior() -> tuple[
    Profile,
    ProfileOption,
]:
    warrior = Profile(
        id="TEST_WARRIOR",
        name="Test Warrior",
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

    crossbow = Wargear(
        id="WG_CROSSBOW",
        name="Crossbow",
    )

    crossbow_option = ProfileOption(
        id="TEST_CROSSBOW",
        name="Crossbow",
        points=2,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=crossbow,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )

    warrior.profile_options.append(
        crossbow_option,
    )

    return warrior, crossbow_option


def test_configured_crossbow_resolves_ranged_weapon_profile():
    warrior, crossbow_option = create_test_warrior()

    configured = ConfiguredProfile(
        profile=warrior,
        selected_options=(crossbow_option,),
    )

    result = resolve_ranged_weapon(
        configured,
    )

    assert result == RangedWeaponProfile(
        wargear_id="WG_CROSSBOW",
    )


def test_profile_without_ranged_weapon_resolves_none():
    warrior, _ = create_test_warrior()

    configured = ConfiguredProfile(
        profile=warrior,
    )

    assert resolve_ranged_weapon(
        configured,
    ) is None

def test_orc_bow_is_recognised_as_ranged_weapon():
    warrior = Profile(
        id="TEST_ORC",
        name="Test Orc",
        points=6,
        movement=6,
        fight=3,
        shooting="5+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    orc_bow = Wargear(
        id="WG_ORC_BOW",
        name="Orc bow",
    )

    warrior.default_wargear.append(
        orc_bow,
    )

    configured = ConfiguredProfile(
        profile=warrior,
    )

    result = resolve_ranged_weapon(
        configured,
    )

    assert result == RangedWeaponProfile(
        wargear_id="WG_ORC_BOW",
        range_inches=18,
        strength=2,
        shots=1,
    )

def test_ranged_weapon_profile_stores_mechanical_values():
    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert weapon.wargear_id == "WG_TEST_BOW"
    assert weapon.range_inches == 24
    assert weapon.strength == 3
    assert weapon.shots == 1


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("range_inches", 0),
        ("range_inches", -1),
        ("strength", 0),
        ("strength", -1),
        ("shots", 0),
        ("shots", -1),
    ),
)
def test_ranged_weapon_profile_rejects_non_positive_mechanics(
    field,
    value,
):
    values = {
        "wargear_id": "WG_TEST_BOW",
        "range_inches": 24,
        "strength": 3,
        "shots": 1,
    }

    values[field] = value

    with pytest.raises(ValueError):
        RangedWeaponProfile(**values)

def test_ranged_weapon_profile_reports_mechanical_completeness():
    incomplete = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
    )

    complete = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert incomplete.is_mechanically_complete is False
    assert complete.is_mechanically_complete is True

def test_elf_bow_has_authoritative_mechanics():
    assert (
        RANGED_WEAPON_PROFILES["WG_ELF_BOW"]
        == RangedWeaponProfile(
            wargear_id="WG_ELF_BOW",
            range_inches=24,
            strength=3,
            shots=1,
        )
    )