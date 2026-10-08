from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_special_rule_wound_reroll import (
    get_shooting_special_rule_wound_reroll,
)
from special_rule import SpecialRule
from wound_reroll import WoundReroll
from wargear import Wargear

def make_profile() -> Profile:
    return Profile(
        id="TEST_SHOOTER",
        name="Test Shooter",
        points=0,
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


def test_profile_wide_poisoned_attacks_applies_to_shooting():
    profile = make_profile()

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="POISONED_ATTACKS",
                name="Poisoned Attacks",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_special_rule_wound_reroll(
        attacker=attacker,
        weapon=weapon,
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )

def test_weapon_specific_poisoned_attacks_applies_only_to_selected_ranged_weapon():
    profile = make_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    poisoned_bow = Wargear(
        id="WG_ORC_BOW",
        name="Orc bow",
        special_rules=[
            poisoned_attacks,
        ],
    )

    normal_bow = Wargear(
        id="WG_NORMAL_BOW",
        name="Normal bow",
    )

    profile.default_wargear.extend(
        (
            poisoned_bow,
            normal_bow,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_shooting_special_rule_wound_reroll(
        attacker=attacker,
        weapon=RangedWeaponProfile(
            wargear_id="WG_ORC_BOW",
            range_inches=18,
            strength=2,
            shots=1,
        ),
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )

def test_weapon_specific_poisoned_attacks_does_not_apply_to_other_ranged_weapon():
    profile = make_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    poisoned_bow = Wargear(
        id="WG_ORC_BOW",
        name="Orc bow",
        special_rules=[
            poisoned_attacks,
        ],
    )

    normal_bow = Wargear(
        id="WG_NORMAL_BOW",
        name="Normal bow",
    )

    profile.default_wargear.extend(
        (
            poisoned_bow,
            normal_bow,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_shooting_special_rule_wound_reroll(
        attacker=attacker,
        weapon=RangedWeaponProfile(
            wargear_id="WG_NORMAL_BOW",
            range_inches=24,
            strength=3,
            shots=1,
        ),
    )

    assert result == WoundReroll()