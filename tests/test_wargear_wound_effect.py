from configured_profile import ConfiguredProfile
from profiles import Profile
from wargear import Wargear
from wargear_wound_effect import get_wargear_wound_modifiers
from wound_modifier import WoundModifier
from melee_weapon_selection import (
    MeleeWeaponSelection,
)

def test_two_handed_weapon_adds_plus_one_to_wound():
    two_handed_weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    profile = Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=3,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        default_wargear=(
            two_handed_weapon,
        ),
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_wargear_wound_modifiers(
        configured_profile
    ) == (
        WoundModifier(
            to_wound=1,
        ),
    )


def test_non_two_handed_wargear_adds_no_wound_modifier():
    hand_weapon = Wargear(
        id="WG_HAND_WEAPON",
        name="Hand Weapon",
    )

    profile = Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=3,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        default_wargear=(
            hand_weapon,
        ),
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_wargear_wound_modifiers(
        configured_profile
    ) == ()

def test_two_handed_wound_bonus_not_applied_when_other_weapon_selected():
    two_handed_weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    hand_weapon = Wargear(
        id="WG_HAND_WEAPON",
        name="Hand Weapon",
    )

    profile = Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=3,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        default_wargear=[
            two_handed_weapon,
            hand_weapon,
        ],
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    selection = MeleeWeaponSelection(
        wargear_id="WG_HAND_WEAPON",
    )

    assert get_wargear_wound_modifiers(
        configured_profile,
        selection=selection,
    ) == ()