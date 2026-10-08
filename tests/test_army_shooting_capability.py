from fractions import Fraction

from army_shooting_capability import (
    sum_expected_shooting_wounds,
)
from configured_profile import ConfiguredProfile
from profiles import Profile
from ranged_weapon_profile import RangedWeaponProfile
from army_shooting_capability import (
    calculate_shooting_output_density,
    get_army_expected_shooting_wounds,
    sum_expected_shooting_wounds,
)
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from shooting_eligibility import (
    ShootingContext,
)
from shooting_eligibility import ShootingContext

def test_sum_expected_shooting_wounds_adds_model_outputs():
    result = sum_expected_shooting_wounds(
        (
            Fraction(1, 6),
            Fraction(1, 3),
            Fraction(1, 2),
        )
    )

    assert result == Fraction(1, 1)


def test_sum_expected_shooting_wounds_empty_army_is_zero():
    result = sum_expected_shooting_wounds(
        ()
    )

    assert result == Fraction(0, 1)

def make_profile(
    *,
    profile_id: str,
    shooting: str = "4+",
    defence: int = 4,
) -> ConfiguredProfile:
    return ConfiguredProfile(
        profile=Profile(
            id=profile_id,
            name=profile_id,
            points=0,
            movement=6,
            fight=4,
            shooting=shooting,
            strength=4,
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


def test_army_expected_shooting_wounds_sums_real_shooters():
    shooter_one = make_profile(
        profile_id="SHOOTER_ONE",
        shooting="4+",
    )

    shooter_two = make_profile(
        profile_id="SHOOTER_TWO",
        shooting="4+",
    )

    defender = make_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_army_expected_shooting_wounds(
        shooters=(
            (shooter_one, weapon),
            (shooter_two, weapon),
        ),
        defender=defender,
    )

    assert result == Fraction(1, 3)

def test_army_expected_shooting_wounds_handles_mixed_shooters():
    normal_shooter = make_profile(
        profile_id="NORMAL",
        shooting="4+",
    )

    expert_profile = make_profile(
        profile_id="EXPERT",
        shooting="4+",
    )

    expert_profile.profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="EXPERT_SHOT",
                name="Expert Shot",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    defender = make_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    normal_bow = RangedWeaponProfile(
        wargear_id="WG_NORMAL_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    stronger_bow = RangedWeaponProfile(
        wargear_id="WG_STRONG_BOW",
        range_inches=24,
        strength=4,
        shots=1,
    )

    result = get_army_expected_shooting_wounds(
        shooters=(
            (
                normal_shooter,
                normal_bow,
            ),
            (
                expert_profile,
                stronger_bow,
            ),
        ),
        defender=defender,
    )

    assert result == Fraction(2, 3)

def test_army_expected_shooting_wounds_excludes_ineligible_shooter():
    eligible_shooter = make_profile(
        profile_id="ELIGIBLE",
        shooting="4+",
    )

    ineligible_shooter = make_profile(
        profile_id="INELIGIBLE",
        shooting="4+",
    )

    defender = make_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_army_expected_shooting_wounds(
        shooters=(
            (
                eligible_shooter,
                weapon,
                ShootingContext(
                    target_distance_inches=12,
                ),
            ),
            (
                ineligible_shooter,
                weapon,
                ShootingContext(
                    engaged_in_combat=True,
                    target_distance_inches=12,
                ),
            ),
        ),
        defender=defender,
    )

    assert result == Fraction(1, 6)

def test_army_expected_shooting_wounds_applies_movement_penalty():
    shooter = make_profile(
        profile_id="MOVED_SHOOTER",
        shooting="4+",
    )

    defender = make_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_army_expected_shooting_wounds(
        shooters=(
            (
                shooter,
                weapon,
                ShootingContext(
                    moved_this_turn=True,
                    target_distance_inches=12,
                ),
            ),
        ),
        defender=defender,
    )

    assert result == Fraction(1, 9)

def test_army_expected_shooting_wounds_deadly_shot_ignores_movement_penalty():
    profile = Profile(
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

    profile.keywords.add(
        "INFANTRY"
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="DEADLY_SHOT",
                name="Deadly Shot",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    shooter = ConfiguredProfile(
        profile=profile,
    )

    defender = make_profile(
        profile_id="DEFENDER",
        defence=4,
    )

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    result = get_army_expected_shooting_wounds(
        shooters=(
            (
                shooter,
                weapon,
                ShootingContext(
                    moved_this_turn=True,
                    target_distance_inches=12,
                ),
            ),
        ),
        defender=defender,
    )

    assert result == Fraction(2, 3)

def test_shooting_output_density_normalises_per_100_points():
    result = calculate_shooting_output_density(
        expected_wounds=Fraction(7, 2),
        army_points=700,
    )

    assert result == Fraction(1, 2)


def test_shooting_output_density_zero_points_returns_zero():
    result = calculate_shooting_output_density(
        expected_wounds=Fraction(3, 1),
        army_points=0,
    )

    assert result == Fraction(0, 1)

def test_shooting_output_density_calibration_examples():
    assert calculate_shooting_output_density(
        expected_wounds=Fraction(0, 1),
        army_points=700,
    ) == Fraction(0, 1)

    assert calculate_shooting_output_density(
        expected_wounds=Fraction(7, 2),
        army_points=700,
    ) == Fraction(1, 2)

    assert calculate_shooting_output_density(
        expected_wounds=Fraction(7, 1),
        army_points=700,
    ) == Fraction(1, 1)

def test_strong_synthetic_shooting_army_produces_high_density():
    shooters = tuple(
        (
            make_profile(
                profile_id=f"ELITE_ARCHER_{index}",
                shooting="3+",
            ),
            RangedWeaponProfile(
                wargear_id="WG_ELF_BOW",
                range_inches=24,
                strength=3,
                shots=1,
            ),
        )
        for index in range(20)
    )

    defender = make_profile(
        profile_id="BENCHMARK_DEFENDER",
        defence=6,
    )

    expected_wounds = get_army_expected_shooting_wounds(
        shooters=shooters,
        defender=defender,
    )

    density = calculate_shooting_output_density(
        expected_wounds=expected_wounds,
        army_points=700,
    )

    assert density == Fraction(
        20,
        63,
    )

def test_extreme_synthetic_shooting_army_produces_higher_density():
    shooters = tuple(
        (
            make_profile(
                profile_id=f"ELITE_ARCHER_{index}",
                shooting="3+",
            ),
            RangedWeaponProfile(
                wargear_id="WG_ELF_BOW",
                range_inches=24,
                strength=3,
                shots=1,
            ),
        )
        for index in range(33)
    )

    defender = make_profile(
        profile_id="BENCHMARK_DEFENDER",
        defence=6,
    )

    expected_wounds = get_army_expected_shooting_wounds(
        shooters=shooters,
        defender=defender,
    )

    density = calculate_shooting_output_density(
        expected_wounds=expected_wounds,
        army_points=700,
    )

    assert density == Fraction(
        11,
        21,
    )