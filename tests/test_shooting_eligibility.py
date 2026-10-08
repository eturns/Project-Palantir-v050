from dataclasses import replace

from configured_profile import ConfiguredProfile
from profiles import Profile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_eligibility import (
    ShootingContext,
    can_shoot,
)
import pytest
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule

def create_test_shooter() -> ConfiguredProfile:
    return ConfiguredProfile(
        profile=Profile(
            id="TEST_SHOOTER",
            name="Test Shooter",
            points=10,
            movement=6,
            fight=3,
            shooting="4+",
            strength=3,
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
    )


def test_weapon_without_movement_restriction_can_shoot_after_moving():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            moved_this_turn=True,
        ),
    ) is True


def test_stationary_only_weapon_cannot_shoot_after_moving():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_WEAPON",
        range_inches=24,
        strength=4,
        shots=1,
        requires_stationary=True,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            moved_this_turn=True,
        ),
    ) is False


def test_stationary_only_weapon_can_shoot_when_stationary():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_WEAPON",
        range_inches=24,
        strength=4,
        shots=1,
        requires_stationary=True,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            moved_this_turn=False,
        ),
    ) is True

def test_mechanically_incomplete_weapon_cannot_shoot():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(),
    ) is False

def test_model_engaged_in_combat_cannot_shoot():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            engaged_in_combat=True,
        ),
    ) is False

def test_target_outside_weapon_range_cannot_be_shot():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            target_distance_inches=25,
        ),
    ) is False

def test_target_at_weapon_range_can_be_shot():
    shooter = create_test_shooter()

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            target_distance_inches=24,
        ),
    ) is True

def test_negative_target_distance_is_rejected():
    with pytest.raises(
        ValueError,
        match="target_distance_inches cannot be negative",
    ):
        ShootingContext(
            target_distance_inches=-1,
        )

def test_deadly_shot_can_shoot_while_engaged_in_combat():
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

    weapon = RangedWeaponProfile(
        wargear_id="WG_TEST_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    )

    assert can_shoot(
        shooter=shooter,
        weapon=weapon,
        context=ShootingContext(
            engaged_in_combat=True,
        ),
    ) is True