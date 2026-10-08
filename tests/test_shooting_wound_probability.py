from fractions import Fraction

from configured_profile import ConfiguredProfile
from profiles import Profile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_wound_probability import (
    get_shooting_wound_probability,
)
from shooting_wound_probability import (
    get_expected_shooting_wounds,
    get_shooting_wound_probability,
)
from wound_modifier import WoundModifier
from database.rule_category import RuleCategory
from lethal_aim_state import (
    LethalAimSpend,
    LethalAimState,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from lethal_aim import (
    get_lethal_aim_hit_modifier,
    get_lethal_aim_in_the_way_modifier,
    get_lethal_aim_wound_modifier,
)
from shooting_to_hit_modifier import (
    get_movement_shooting_modifier,
)
from wound_reroll import WoundReroll
from wargear import Wargear

def create_profile(
    *,
    profile_id: str,
    shooting: str = "4+",
    defence: int = 4,
) -> ConfiguredProfile:
    return ConfiguredProfile(
        profile=Profile(
            id=profile_id,
            name=profile_id,
            points=10,
            movement=6,
            fight=3,
            shooting=shooting,
            strength=3,
            defence=defence,
            attacks=1,
            wounds=1,
            courage="6+",
            intelligence="6+",
            might=0,
            will=0,
            fate=0,
            max_in_army=0,
        )
    )


def test_shooting_wound_probability_combines_hit_and_wound():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
    )

    assert result == Fraction(1, 6)

def test_expected_shooting_wounds_uses_weapon_shots():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=3,
    )

    result = get_expected_shooting_wounds(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
    )

    assert result == Fraction(1, 2)

def test_shooting_wound_probability_applies_in_the_way():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4,),
    )

    assert result == Fraction(1, 12)

def test_shooting_wound_probability_applies_multiple_in_the_way_checks():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4, 4),
    )

    assert result == Fraction(1, 24)

def test_shooting_wound_probability_applies_to_hit_modifier():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        to_hit_modifier=1,
    )

    assert result == Fraction(2, 9)

def test_shooting_wound_probability_applies_to_wound_modifier():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        wound_modifier=WoundModifier(
            to_wound=1,
        ),
    )

    assert result == Fraction(1, 4)

def test_lethal_aim_modifier_improves_shooting_wound_probability():
    attacker_profile = Profile(
        id="NARZUG_TEST",
        name="Narzug Test",
        points=55,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=2,
        will=2,
        fate=1,
        max_in_army=1,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="LETHAL_AIM",
                name="Lethal Aim",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    lethal_aim_modifier = (
        get_lethal_aim_wound_modifier(
            attacker,
            LethalAimState(),
            context=WoundContext(
                attack_type=WoundAttackType.SHOOTING,
            ),
            spend=LethalAimSpend.TO_WOUND,
        )
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        wound_modifier=lethal_aim_modifier,
    )

    assert result == Fraction(1, 4)

def test_lethal_aim_hit_modifier_improves_shooting_wound_probability():
    attacker_profile = Profile(
        id="NARZUG_TEST",
        name="Narzug Test",
        points=55,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=2,
        will=2,
        fate=1,
        max_in_army=1,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="LETHAL_AIM",
                name="Lethal Aim",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    lethal_aim_modifier = (
        get_lethal_aim_hit_modifier(
            attacker,
            LethalAimState(),
            spend=LethalAimSpend.TO_HIT,
        )
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        to_hit_modifier=lethal_aim_modifier,
    )

    assert result == Fraction(2, 9)

def test_shooting_wound_probability_applies_in_the_way_modifier():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4,),
        in_the_way_modifier=1,
    )

    assert result == Fraction(1, 9)

def test_lethal_aim_in_the_way_modifier_improves_shooting_wound_probability():
    attacker_profile = Profile(
        id="NARZUG_TEST",
        name="Narzug Test",
        points=55,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=2,
        will=2,
        fate=1,
        max_in_army=1,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="LETHAL_AIM",
                name="Lethal Aim",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    lethal_aim_modifier = (
        get_lethal_aim_in_the_way_modifier(
            attacker,
            LethalAimState(),
            spend=LethalAimSpend.IN_THE_WAY,
        )
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4,),
        in_the_way_modifier=lethal_aim_modifier,
    )

    assert result == Fraction(1, 9)

def test_expected_shooting_wounds_applies_modifiers_and_in_the_way():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=3,
    )

    result = get_expected_shooting_wounds(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        to_hit_modifier=1,
        in_the_way_required_rolls=(4,),
        in_the_way_modifier=1,
        wound_modifier=WoundModifier(
            to_wound=1,
        ),
    )

    assert result == Fraction(2, 3)

def test_expected_shooting_wounds_applies_lethal_aim_to_wound():
    attacker_profile = Profile(
        id="NARZUG_TEST",
        name="Narzug Test",
        points=55,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=2,
        will=2,
        fate=1,
        max_in_army=1,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="LETHAL_AIM",
                name="Lethal Aim",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=3,
    )

    lethal_aim_modifier = (
        get_lethal_aim_wound_modifier(
            attacker,
            LethalAimState(),
            context=WoundContext(
                attack_type=WoundAttackType.SHOOTING,
            ),
            spend=LethalAimSpend.TO_WOUND,
        )
    )

    result = get_expected_shooting_wounds(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        wound_modifier=lethal_aim_modifier,
    )

    assert result == Fraction(3, 4)

def test_shooting_wound_probability_applies_modifier_to_multiple_in_the_way_checks():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4, 4),
        in_the_way_modifier=1,
    )

    assert result == Fraction(2, 27)

def test_expert_shot_doubles_expected_shooting_wounds():
    attacker_profile = Profile(
        id="EXPERT_SHOT_TEST",
        name="Expert Shot Test",
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

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="EXPERT_SHOT",
                name="Expert Shot",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_expected_shooting_wounds(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
    )

    assert result == Fraction(1, 3)

def test_deadly_shot_infantry_ignores_moving_penalty_in_shooting_probability():
    attacker_profile = Profile(
        id="LEGOLAS_TEST",
        name="Legolas Test",
        points=0,
        movement=6,
        fight=6,
        shooting="3+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="4+",
        might=3,
        will=2,
        fate=3,
        max_in_army=1,
    )

    attacker_profile.keywords.add(
        "INFANTRY"
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="DEADLY_SHOT",
                name="Deadly Shot",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    movement_modifier = (
        get_movement_shooting_modifier(
            attacker,
            moved_this_turn=True,
        )
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        to_hit_modifier=movement_modifier,
    )

    assert result == Fraction(2, 9)

def test_shooting_wound_probability_applies_natural_one_wound_reroll():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="4+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        wound_reroll=WoundReroll(
            reroll_natural_ones=True,
        ),
    )

    assert result == Fraction(7, 36)

def test_weapon_specific_poisoned_attacks_applies_automatically():
    attacker_profile = Profile(
        id="NARZUG_TEST",
        name="Narzug Test",
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

    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.default_wargear.append(
        Wargear(
            id="WG_ORC_BOW",
            name="Orc bow",
            special_rules=[
                poisoned_attacks,
            ],
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_ORC_BOW",
        range_inches=18,
        strength=2,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
    )

    assert result > Fraction(1, 12)

def test_sharpshooter_bypasses_cavalry_part_in_the_way_only():
    attacker_profile = Profile(
        id="TAURIEL_TEST",
        name="Tauriel Test",
        points=0,
        movement=6,
        fight=6,
        shooting="3+",
        strength=4,
        defence=5,
        attacks=3,
        wounds=2,
        courage="5+",
        intelligence="4+",
        might=3,
        will=2,
        fate=2,
        max_in_army=1,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="SHARPSHOOTER",
                name="Sharpshooter",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4,),
        cavalry_part_in_the_way_required_roll=4,
        target_is_cavalry=True,
    )

    assert result == Fraction(1, 9)

def test_non_sharpshooter_applies_cavalry_part_in_the_way_test():
    attacker = create_profile(
        profile_id="ATTACKER",
        shooting="3+",
    )

    defender = create_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(4,),
        cavalry_part_in_the_way_required_roll=4,
        target_is_cavalry=True,
    )

    assert result == Fraction(1, 18)