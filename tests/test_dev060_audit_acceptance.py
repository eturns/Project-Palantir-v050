from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from mount import Mount
from profile_classification import ModelType
from profile_option import ProfileOption
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from profiles import Profile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule

def create_base_hero() -> Profile:
    return Profile(
        id="TEST_HERO",
        name="Test Hero",
        points=80,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="5+",
        might=2,
        will=1,
        fate=1,
        max_in_army=1,
        model_types={
            ModelType.INFANTRY,
        },
        base_size_mm=25,
    )


def test_optional_mount_resolves_static_configured_state():
    profile = create_base_hero()

    horse = Mount(
        id="HORSE",
        name="Horse",
        base_size_mm=40,
    )

    mounted_option = ProfileOption(
        id="HORSE_OPTION",
        name="Horse",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=horse,
            ),
        ),
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
                model_type_override=ModelType.CAVALRY,
                base_size_override_mm=40,
            ),
        ),
    )

    profile.profile_options.append(
        mounted_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            mounted_option,
        ),
    )

    assert configured_profile.points == 90
    assert configured_profile.effective_mount is horse
    assert configured_profile.effective_movement == 10
    assert configured_profile.effective_model_types == {
        ModelType.CAVALRY
    }
    assert configured_profile.effective_base_size_mm == 40

    assert profile.points == 80
    assert profile.movement == 6
    assert profile.model_types == {
        ModelType.INFANTRY
    }
    assert profile.base_size_mm == 25

def test_optional_defence_configuration_resolves_effective_defence():
    profile = create_base_hero()

    shield_option = ProfileOption(
        id="SHIELD_OPTION",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

    profile.profile_options.append(
        shield_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            shield_option,
        ),
    )

    assert configured_profile.points == 85
    assert configured_profile.effective_defence == 7
    assert profile.defence == 6


def test_optional_shooting_configuration_resolves_effective_shooting():
    profile = create_base_hero()

    shooting_option = ProfileOption(
        id="SHOOTING_OPTION",
        name="Improved shooting",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                shooting_override="3+",
            ),
        ),
    )

    profile.profile_options.append(
        shooting_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            shooting_option,
        ),
    )

    assert configured_profile.points == 85
    assert configured_profile.effective_shooting == "3+"
    assert profile.shooting == "4+"


def test_option_granted_rule_resolves_effective_static_rules():
    profile = create_base_hero()

    granted_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="TEST_GRANTED_RULE",
            name="Test Granted Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    rule_option = ProfileOption(
        id="RULE_OPTION",
        name="Rule option",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    granted_assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(
        rule_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            rule_option,
        ),
    )

    assert configured_profile.effective_special_rules == [
        granted_assignment
    ]

    assert profile.special_rules == []