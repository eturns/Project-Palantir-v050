from configured_profile import ConfiguredProfile
from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from profiles import Profile
from wargear import Wargear
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from melee_weapon_selection import (
    MeleeWeaponSelection,
)

def create_test_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name="Test Profile",
        points=10,
        movement=6,
        fight=4,
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
    )


def test_two_handed_weapon_reduces_configured_duel_probability():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    two_handed_weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    attacker_profile.default_wargear.append(
        two_handed_weapon
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result.attacker_win_probability < 0.5

def test_burly_removes_configured_two_handed_duel_penalty():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    two_handed_weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    burly = SpecialRule(
        id="BURLY",
        name="Burly",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.default_wargear.append(
        two_handed_weapon
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=burly,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result.attacker_win_probability == 0.5

def test_configured_duel_uses_selected_hand_weapon():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    attacker_profile.default_wargear.extend(
        (
            Wargear(
                id="WG_TWO_HANDED_WEAPON",
                name="Two-handed Weapon",
            ),
            Wargear(
                id="WG_HAND_WEAPON",
                name="Hand Weapon",
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
        attacker_selection=MeleeWeaponSelection(
            wargear_id="WG_HAND_WEAPON",
        ),
    )

    assert result.attacker_win_probability == 0.5

def test_slayer_pair_proximity_removes_two_handed_duel_penalty():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    attacker_profile.default_wargear.append(
        Wargear(
            id="WG_TWO_HANDED_WEAPON",
            name="Two-handed Weapon",
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
        attacker_additional_burly=True,
    )

    assert result.attacker_win_probability == 0.5