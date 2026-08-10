from configured_profile import ConfiguredProfile
from duel_modifier import DuelModifier
from profiles import Profile
from wargear import Wargear
from wargear_duel_effect import get_wargear_duel_modifiers
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from melee_weapon_selection import (
    MeleeWeaponSelection,
)
def test_two_handed_weapon_adds_duel_penalty():
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

    assert get_wargear_duel_modifiers(
        configured_profile
    ) == (
        DuelModifier(
            value=-1,
            ignored_on_natural_six=True,
        ),
    )


def test_non_two_handed_wargear_adds_no_duel_modifier():
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

    assert get_wargear_duel_modifiers(
        configured_profile
    ) == ()

def test_burly_removes_two_handed_duel_penalty():
    two_handed_weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    burly = SpecialRule(
        id="BURLY",
        name="Burly",
        category=RuleCategory.SPECIAL,
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
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=burly,
                parameter=None,
            )
        ],
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_wargear_duel_modifiers(
        configured_profile
    ) == ()

def test_two_handed_duel_penalty_not_applied_when_other_weapon_selected():
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

    assert get_wargear_duel_modifiers(
        configured_profile,
        selection=selection,
    ) == ()

def test_additional_burly_removes_two_handed_duel_penalty():
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

    assert get_wargear_duel_modifiers(
        configured_profile,
        additional_burly=True,
    ) == ()