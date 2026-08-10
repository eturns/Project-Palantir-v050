from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from special_rule_wound_effect import (
    get_special_rule_wound_reroll,
)
from wound_reroll import WoundReroll
from melee_weapon_selection import MeleeWeaponSelection
from wargear import Wargear

from wound_attack_type import WoundAttackType
from wound_context import WoundContext

def create_test_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
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

def test_venom_grants_failed_wound_reroll():
    profile = create_test_profile()

    venom = SpecialRule(
        id="VENOM",
        name="Venom",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=venom,
            parameter=None,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_special_rule_wound_reroll(
        configured_profile
    ) == WoundReroll(
        reroll_failed=True,
    )

def test_bane_of_kings_grants_failed_wound_reroll():
    profile = create_test_profile()

    bane_of_kings = SpecialRule(
        id="BANE_OF_KINGS",
        name="Bane of Kings",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=bane_of_kings,
            parameter=None,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_special_rule_wound_reroll(
        configured_profile
    ) == WoundReroll(
        reroll_failed=True,
    )

def test_poisoned_attacks_grants_natural_one_wound_reroll():
    profile = create_test_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=poisoned_attacks,
            parameter=None,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_special_rule_wound_reroll(
        configured_profile
    ) == WoundReroll(
        reroll_natural_ones=True,
    )

def test_selected_poisoned_weapon_grants_natural_one_reroll():
    profile = create_test_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    fangs = Wargear(
        id="WG_FANGS",
        name="Fangs",
        special_rules=[
            poisoned_attacks,
        ],
    )

    profile.default_wargear.append(
        fangs
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_wound_reroll(
        configured_profile,
        selection=MeleeWeaponSelection(
            wargear_id="WG_FANGS",
        ),
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )

def test_unselected_poisoned_weapon_does_not_grant_reroll():
    profile = create_test_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    fangs = Wargear(
        id="WG_FANGS",
        name="Fangs",
        special_rules=[
            poisoned_attacks,
        ],
    )

    hand_weapon = Wargear(
        id="WG_HAND_WEAPON",
        name="Hand Weapon",
    )

    profile.default_wargear.extend(
        (
            fangs,
            hand_weapon,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_wound_reroll(
        configured_profile,
        selection=MeleeWeaponSelection(
            wargear_id="WG_HAND_WEAPON",
        ),
    )

    assert result == WoundReroll()

def test_ancient_enemies_grants_reroll_against_matching_keyword():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    ancient_enemies = SpecialRule(
        id="ANCIENT_ENEMIES",
        name="Ancient Enemies",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=ancient_enemies,
            parameter="ORC",
        )
    )

    defender_profile.keywords.add("ORC")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_reroll(
        attacker,
        defender=defender,
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )

def test_ancient_enemies_does_not_apply_against_nonmatching_keyword():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    ancient_enemies = SpecialRule(
        id="ANCIENT_ENEMIES",
        name="Ancient Enemies",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=ancient_enemies,
            parameter="ORC",
        )
    )

    defender_profile.keywords.add("DWARF")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_reroll(
        attacker,
        defender=defender,
    )

    assert result == WoundReroll()

def test_venom_grants_failed_reroll_for_strikes():
    profile = create_test_profile()

    venom = SpecialRule(
        id="VENOM",
        name="Venom",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=venom,
            parameter=None,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_wound_reroll(
        configured_profile,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    )

    assert result == WoundReroll(
        reroll_failed=True,
    )

def test_venom_does_not_grant_failed_reroll_for_shooting():
    profile = create_test_profile()

    venom = SpecialRule(
        id="VENOM",
        name="Venom",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=venom,
            parameter=None,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_wound_reroll(
        configured_profile,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result == WoundReroll()

def test_poisoned_melee_weapon_does_not_apply_to_shooting():
    profile = create_test_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    fangs = Wargear(
        id="WG_FANGS",
        name="Fangs",
        special_rules=[
            poisoned_attacks,
        ],
    )

    profile.default_wargear.append(
        fangs
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_wound_reroll(
        configured_profile,
        selection=MeleeWeaponSelection(
            wargear_id="WG_FANGS",
        ),
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result == WoundReroll()

def test_profile_wide_poisoned_attacks_applies_to_shooting():
    profile = create_test_profile()

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=poisoned_attacks,
            parameter=None,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_wound_reroll(
        configured_profile,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result == WoundReroll(
        reroll_natural_ones=True,
    )

def test_slayer_of_men_grants_failed_reroll_against_hero():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    slayer_of_men = SpecialRule(
        id="SLAYER_OF_MEN",
        name="Slayer of Men",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=slayer_of_men,
            parameter=None,
        )
    )

    defender_profile.keywords.add("HERO")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_reroll(
        attacker,
        defender=defender,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    )

    assert result == WoundReroll(
        reroll_failed=True,
    )


def test_slayer_of_men_does_not_apply_against_non_hero():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    slayer_of_men = SpecialRule(
        id="SLAYER_OF_MEN",
        name="Slayer of Men",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=slayer_of_men,
            parameter=None,
        )
    )

    defender_profile.keywords.add("WARRIOR")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_reroll(
        attacker,
        defender=defender,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    )

    assert result == WoundReroll()


def test_slayer_of_men_does_not_apply_to_shooting():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    slayer_of_men = SpecialRule(
        id="SLAYER_OF_MEN",
        name="Slayer of Men",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=slayer_of_men,
            parameter=None,
        )
    )

    defender_profile.keywords.add("HERO")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_reroll(
        attacker,
        defender=defender,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result == WoundReroll()