from army import Army
from configured_profile import ConfiguredProfile
from profiles import Profile

from army_offence_capability import (
    calculate_army_offensive_combat_score,
)
import pytest
from army_offence_capability import (
    calculate_army_offensive_combat_score,
    calculate_army_offensive_output_density,
)
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from wargear import Wargear
from combat_benchmark import CombatBenchmark
from wound_context import WoundContext
from wound_attack_type import WoundAttackType

def test_army_offence_uses_configured_profiles():
    profile = Profile(
        id="TEST",
        name="Test Fighter",
        points=10,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=10,
    )

    army = Army()

    army.add_profile(
        profile,
        quantity=1,
    )

    result = calculate_army_offensive_combat_score(
        army,
    )

    assert result > 0.0

def test_army_offensive_output_density_is_points_normalised():
    profile = Profile(
        id="TEST",
        name="Test Fighter",
        points=20,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=10,
    )

    army = Army()

    army.add_profile(
        profile,
        quantity=2,
    )

    average_score = calculate_army_offensive_combat_score(
        army,
    )

    result = calculate_army_offensive_output_density(
        army,
    )

    assert result == pytest.approx(
        average_score * 5
    )

def test_army_offence_rewards_burly_with_two_handed_weapon():
    base_profile = Profile(
        id="BASE",
        name="Base Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    burly_profile = Profile(
        id="BURLY",
        name="Burly Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    two_handed_weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    base_profile.default_wargear.append(
        two_handed_weapon,
    )

    burly_profile.default_wargear.append(
        two_handed_weapon,
    )

    burly_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="BURLY",
                name="Burly",
                category=RuleCategory.SPECIAL,
            ),
            parameter=None,
        )
    )

    base_army = Army()
    base_army.add_profile(
        base_profile,
        quantity=1,
    )

    burly_army = Army()
    burly_army.add_profile(
        burly_profile,
        quantity=1,
    )

    base_score = calculate_army_offensive_output_density(
        base_army,
    )

    burly_score = calculate_army_offensive_output_density(
        burly_army,
    )

    assert burly_score > base_score

def test_army_offence_can_reflect_charge_opportunity():
    savage_profile = Profile(
        id="SAVAGE",
        name="Savage Fighter",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    savage_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="SAVAGE_HUNTERS",
                name="Savage Hunters",
                category=RuleCategory.OFFENCE,
            ),
            parameter=None,
        )
    )

    army = Army()
    army.add_profile(
        savage_profile,
        quantity=1,
    )

    never_charges = calculate_army_offensive_output_density(
        army,
        charge_probability=0.0,
    )

    always_charges = calculate_army_offensive_output_density(
        army,
        charge_probability=1.0,
    )

    assert always_charges > never_charges

def test_army_offence_default_represents_proactive_charge_state():
    savage_profile = Profile(
        id="SAVAGE_DEFAULT",
        name="Savage Fighter",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    savage_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="SAVAGE_HUNTERS",
                name="Savage Hunters",
                category=RuleCategory.OFFENCE,
            ),
            parameter=None,
        )
    )

    army = Army()
    army.add_profile(
        savage_profile,
        quantity=1,
    )

    default_score = calculate_army_offensive_output_density(
        army,
    )

    charging_score = calculate_army_offensive_output_density(
        army,
        charge_probability=1.0,
    )

    assert default_score == pytest.approx(
        charging_score
    )

def test_army_offence_rewards_mighty_blow_against_multi_wound_target():
    base_profile = Profile(
        id="BASE_MULTI",
        name="Base Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    mighty_blow_profile = Profile(
        id="MIGHTY_BLOW_MULTI",
        name="Mighty Blow Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    mighty_blow_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="MIGHTY_BLOW",
                name="Mighty Blow",
                category=RuleCategory.OFFENCE,
            ),
            parameter=None,
        )
    )

    base_army = Army()
    base_army.add_profile(
        base_profile,
        quantity=1,
    )

    mighty_blow_army = Army()
    mighty_blow_army.add_profile(
        mighty_blow_profile,
        quantity=1,
    )

    elite_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
    )

    base_score = calculate_army_offensive_output_density(
        base_army,
        benchmark=elite_benchmark,
    )

    mighty_blow_score = calculate_army_offensive_output_density(
        mighty_blow_army,
        benchmark=elite_benchmark,
    )

    assert mighty_blow_score > base_score

def test_army_offence_rewards_drain_soul_against_multi_wound_target():
    base_profile = Profile(
        id="BASE_DRAIN",
        name="Base Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    drain_soul_profile = Profile(
        id="DRAIN_SOUL_TEST",
        name="Drain Soul Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    drain_soul_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="DRAIN_SOUL",
                name="Drain Soul",
                category=RuleCategory.OFFENCE,
            ),
            parameter=None,
        )
    )

    base_army = Army()
    base_army.add_profile(
        base_profile,
        quantity=1,
    )

    drain_soul_army = Army()
    drain_soul_army.add_profile(
        drain_soul_profile,
        quantity=1,
    )

    elite_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=3,
    )

    base_score = calculate_army_offensive_output_density(
        base_army,
        benchmark=elite_benchmark,
    )

    drain_soul_score = calculate_army_offensive_output_density(
        drain_soul_army,
        benchmark=elite_benchmark,
    )

    assert drain_soul_score > base_score

def test_army_offence_rewards_venom_against_multi_wound_target():
    base_profile = Profile(
        id="BASE_VENOM",
        name="Base Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    venom_profile = Profile(
        id="VENOM_TEST",
        name="Venom Fighter",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    venom_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="VENOM",
                name="Venom",
                category=RuleCategory.OFFENCE,
            ),
            parameter=None,
        )
    )

    base_army = Army()
    base_army.add_profile(
        base_profile,
        quantity=1,
    )

    venom_army = Army()
    venom_army.add_profile(
        venom_profile,
        quantity=1,
    )

    elite_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
    )

    base_score = calculate_army_offensive_output_density(
        base_army,
        benchmark=elite_benchmark,
    )

    venom_score = calculate_army_offensive_output_density(
        venom_army,
        benchmark=elite_benchmark,
    )

    assert venom_score > base_score