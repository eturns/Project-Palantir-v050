from fractions import Fraction

from configured_profile import ConfiguredProfile
from configured_wound_probability import (
    calculate_configured_wound_probability,
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
from wound_context import WoundContext
from wound_attack_type import WoundAttackType

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


def test_two_handed_weapon_improves_configured_wound_probability():
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

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result == Fraction(2, 3)

def test_burly_preserves_two_handed_wound_bonus():
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

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result == Fraction(2, 3)

def test_configured_wound_uses_selected_hand_weapon():
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

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
        attacker_selection=MeleeWeaponSelection(
            wargear_id="WG_HAND_WEAPON",
        ),
    )

    assert result == Fraction(1, 2)

def test_configured_wound_probability_applies_bane_of_kings():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    bane_of_kings = SpecialRule(
        id="BANE_OF_KINGS",
        name="Bane of Kings",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=bane_of_kings,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result == Fraction(3, 4)

def test_configured_wound_probability_applies_ancient_enemies():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

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

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result == Fraction(7, 12)

def test_configured_wound_probability_applies_hatred():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    hatred = SpecialRule(
        id="HATRED",
        name="Hatred",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=hatred,
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

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result == Fraction(2, 3)

def test_configured_wound_probability_applies_backstabbers():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    backstabbers = SpecialRule(
        id="BACKSTABBERS",
        name="Backstabbers",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=backstabbers,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
        context=WoundContext(
            defender_trapped=True,
        ),
    )

    assert result == Fraction(2, 3)

def test_configured_wound_probability_applies_blades_of_the_dead():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    defender_profile.defence = 6
    defender_profile.courage = "8+"

    blades_of_the_dead = SpecialRule(
        id="BLADES_OF_THE_DEAD",
        name="Blades of the Dead",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=blades_of_the_dead,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result == Fraction(2, 3)

def test_configured_wound_probability_does_not_apply_venom_to_shooting():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    venom = SpecialRule(
        id="VENOM",
        name="Venom",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=venom,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result == Fraction(1, 2)

def test_configured_wound_probability_applies_bane_of_kings_to_shooting():
    attacker_profile = create_test_profile(
        "ATTACKER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    bane_of_kings = SpecialRule(
        id="BANE_OF_KINGS",
        name="Bane of Kings",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=bane_of_kings,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = calculate_configured_wound_probability(
        attacker=attacker,
        defender=defender,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result == Fraction(3, 4)