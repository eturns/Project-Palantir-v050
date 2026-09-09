from army_entry import ArmyEntry
from configured_profile import ConfiguredProfile
from profile_option import ProfileOption
from profiles import Profile
from army import Army
from configured_state_effect import ConfiguredStateEffect
from database.rule_category import RuleCategory
from profile_classification import ModelType
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from mount import Mount
from model_platform import Platform, PlatformType
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from profile_option_platform_assignment import (
    ProfileOptionPlatformAssignment,
)
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from wargear import Wargear
from army_definition import (
    ArmyDefinition,
    ArmyEntryDefinition,
)
from army_builder import build_army_from_definition

from army_list import ArmyList
from faction import Faction
def create_profile() -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_army_entry_preserves_configured_profile():
    profile = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    entry = ArmyEntry(
        configured_profile=configured_profile,
        quantity=1,
    )

    assert entry.configured_profile is configured_profile


def test_army_entry_exposes_canonical_profile_from_configuration():
    profile = create_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    entry = ArmyEntry(
        configured_profile=configured_profile,
        quantity=1,
    )

    assert entry.profile is profile

def test_army_entry_wraps_legacy_profile_in_configured_profile():
    profile = create_profile()

    entry = ArmyEntry(
        profile=profile,
        quantity=1,
    )

    assert isinstance(
        entry.configured_profile,
        ConfiguredProfile,
    )

    assert entry.configured_profile.profile is profile
    assert entry.configured_profile.selected_options == ()
    assert entry.profile is profile

def test_army_entry_rejects_profile_and_configured_profile_together():
    profile = create_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    try:
        ArmyEntry(
            profile=profile,
            configured_profile=configured_profile,
            quantity=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when ArmyEntry "
            "receives both profile and configured_profile."
        )

def test_army_entry_total_points_uses_configured_profile_points():
    profile = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    entry = ArmyEntry(
        configured_profile=configured_profile,
        quantity=1,
    )

    assert entry.total_points() == 30


def test_army_entry_total_points_applies_quantity_to_configured_points():
    profile = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    entry = ArmyEntry(
        configured_profile=configured_profile,
        quantity=3,
    )

    assert entry.total_points() == 90


def test_army_entry_configured_points_do_not_mutate_base_profile():
    profile = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    entry = ArmyEntry(
        configured_profile=configured_profile,
        quantity=2,
    )

    assert entry.total_points() == 60
    assert profile.points == 20

def test_army_add_configured_profile_preserves_configuration():
    profile = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    assert len(army.entries) == 1
    assert army.entries[0].configured_profile is configured_profile
    assert army.entries[0].quantity == 2


def test_army_add_profile_still_wraps_bare_profile():
    profile = create_profile()

    army = Army()

    army.add_profile(
        profile,
        quantity=2,
    )

    assert len(army.entries) == 1
    assert army.entries[0].profile is profile
    assert army.entries[0].configured_profile.profile is profile
    assert army.entries[0].configured_profile.selected_options == ()

def test_army_total_points_uses_configured_entry_points():
    profile = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    assert army.total_points() == 60


def test_army_total_points_combines_configured_and_unconfigured_entries():
    configured_base = create_profile()

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
    )

    configured_base.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=configured_base,
        selected_options=(
            option,
        ),
    )

    plain_profile = Profile(
        id="PLAIN_PROFILE",
        name="Plain Profile",
        points=15,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    army.add_profile(
        plain_profile,
        quantity=1,
    )

    assert army.total_points() == 75

def test_army_average_movement_uses_effective_configured_movement():
    profile = create_profile()

    mounted_option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
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

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    assert army.average_movement() == 10


def test_army_fast_model_count_uses_effective_configured_movement():
    profile = create_profile()

    mounted_option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
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

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    assert army.fast_model_count() == 2
    assert army.standard_model_count() == 0

def test_army_average_defence_uses_effective_configured_defence():
    profile = create_profile()

    shield_option = ProfileOption(
        id="SHIELD",
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

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    assert army.average_defence() == 7


def test_army_high_defence_count_uses_effective_configured_defence():
    profile = Profile(
        id="LOW_DEFENCE_PROFILE",
        name="Low Defence Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    shield_option = ProfileOption(
        id="SHIELD",
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

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    assert army.high_defence_model_count() == 2

def test_army_entry_preserves_effective_model_type():
    profile = create_profile()

    mounted_option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                model_type_override=ModelType.CAVALRY,
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

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert army.entries[0].configured_profile.effective_model_types == {
        ModelType.CAVALRY
    }


def test_army_entry_preserves_effective_shooting():
    profile = create_profile()

    shooting_option = ProfileOption(
        id="SHOOTING",
        name="Shooting",
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

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert (
        army.entries[0]
        .configured_profile
        .effective_shooting
        == "3+"
    )


def test_army_entry_preserves_effective_base_size():
    profile = create_profile()

    base_option = ProfileOption(
        id="BASE_SIZE",
        name="Base size",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    profile.profile_options.append(
        base_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            base_option,
        ),
    )

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert (
        army.entries[0]
        .configured_profile
        .effective_base_size_mm
        == 40
    )


def test_army_entry_preserves_effective_special_rules():
    profile = create_profile()

    granted_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="GRANTED_RULE",
            name="Granted Rule",
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

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert (
        army.entries[0]
        .configured_profile
        .effective_special_rules
        == [granted_assignment]
    )

def test_army_entry_preserves_effective_wargear():
    profile = create_profile()

    shield = Wargear(
        id="SHIELD",
        name="Shield",
    )

    wargear_option = ProfileOption(
        id="SHIELD_OPTION",
        name="Shield",
        points=5,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )

    profile.profile_options.append(
        wargear_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            wargear_option,
        ),
    )

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert (
        army.entries[0]
        .configured_profile
        .effective_wargear
        == (shield,)
    )


def test_army_entry_preserves_effective_mount():
    profile = create_profile()

    horse = Mount(
        id="HORSE",
        name="Horse",
        base_size_mm=40,
    )

    mount_option = ProfileOption(
        id="HORSE_OPTION",
        name="Horse",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=horse,
            ),
        ),
    )

    profile.profile_options.append(
        mount_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            mount_option,
        ),
    )

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert (
        army.entries[0]
        .configured_profile
        .effective_mount
        is horse
    )


def test_army_entry_preserves_effective_platform():
    profile = create_profile()

    platform = Platform(
        id="TEST_PLATFORM",
        name="Test Platform",
        platform_type=PlatformType.VEHICLE,
    )

    platform_option = ProfileOption(
        id="PLATFORM_OPTION",
        name="Platform",
        points=20,
        platform_assignments=(
            ProfileOptionPlatformAssignment(
                platform=platform,
            ),
        ),
    )

    profile.profile_options.append(
        platform_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            platform_option,
        ),
    )

    army = Army()
    army.add_configured_profile(
        configured_profile,
    )

    assert (
        army.entries[0]
        .configured_profile
        .effective_platform
        is platform
    )

def test_army_entry_get_attribute_uses_effective_defence():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    shield_option = ProfileOption(
        id="SHIELD",
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

    entry = ArmyEntry(
        configured_profile=configured_profile,
    )

    assert entry.get_attribute("defence") == 6
    assert profile.defence == 5


def test_army_entry_get_attribute_uses_effective_movement():
    profile = create_profile()

    mounted_option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
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

    entry = ArmyEntry(
        configured_profile=configured_profile,
    )

    assert entry.get_attribute("movement") == 10
    assert profile.movement == 6


def test_army_entry_get_attribute_falls_back_to_base_profile():
    profile = create_profile()

    entry = ArmyEntry(
        profile=profile,
    )

    assert entry.get_attribute("strength") == 4


def test_army_entry_total_attribute_uses_effective_value():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    shield_option = ProfileOption(
        id="SHIELD",
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

    entry = ArmyEntry(
        configured_profile=configured_profile,
        quantity=3,
    )

    assert entry.total_attribute("defence") == 18

def test_army_highest_defence_returns_configured_entry():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=2,
            ),
        ),
    )

    profile.profile_options.append(shield_option)

    plain = ConfiguredProfile(
        profile=profile,
    )

    shielded = ConfiguredProfile(
        profile=profile,
        selected_options=(shield_option,),
    )

    army = Army()

    army.add_configured_profile(plain)
    army.add_configured_profile(shielded)

    highest = army.highest_defence()

    assert highest.configured_profile is shielded
    assert highest.get_attribute("defence") == 7

def test_same_profile_can_have_multiple_distinct_configurations():
    profile = Profile(
        id="GENERIC_HERO",
        name="Generic Hero",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="6+",
        might=2,
        will=1,
        fate=1,
        max_in_army=0,
    )

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

    mounted_option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=10,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            shield_option,
            mounted_option,
        )
    )

    shielded = ConfiguredProfile(
        profile=profile,
        selected_options=(
            shield_option,
        ),
    )

    mounted = ConfiguredProfile(
        profile=profile,
        selected_options=(
            mounted_option,
        ),
    )

    army = Army()

    army.add_configured_profile(
        shielded,
    )

    army.add_configured_profile(
        mounted,
    )

    assert len(army.entries) == 2

    shielded_entry = army.entries[0]
    mounted_entry = army.entries[1]

    assert (
        shielded_entry.profile
        is mounted_entry.profile
    )

    assert (
        shielded_entry.configured_profile
        is shielded
    )

    assert (
        mounted_entry.configured_profile
        is mounted
    )

    assert (
        shielded_entry.configured_profile
        is not mounted_entry.configured_profile
    )

    assert (
        shielded_entry.get_attribute("defence")
        == 6
    )

    assert (
        mounted_entry.get_attribute("defence")
        == 5
    )

    assert (
        shielded_entry.get_attribute("movement")
        == 6
    )

    assert (
        mounted_entry.get_attribute("movement")
        == 10
    )

    assert shielded_entry.total_points() == 55
    assert mounted_entry.total_points() == 60

def test_build_army_preserves_multiple_configurations_of_same_profile():
    profile = create_profile()

    shield_option = ProfileOption(
        id="SHIELD_OPTION",
        name="Shield",
        points=5,
        external_id="EXT_SHIELD",
    )

    mounted_option = ProfileOption(
        id="MOUNTED_OPTION",
        name="Mounted",
        points=10,
        external_id="EXT_MOUNTED",
    )

    profile.profile_options.extend(
        (
            shield_option,
            mounted_option,
        )
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Configured Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id=profile.id,
                quantity=1,
                external_option_ids=(
                    "EXT_SHIELD",
                ),
            ),
            ArmyEntryDefinition(
                profile_id=profile.id,
                quantity=1,
                external_option_ids=(
                    "EXT_MOUNTED",
                ),
            ),
        ],
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
    )

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={
            profile.id: profile,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
        profile_options_by_external_id={
            "EXT_SHIELD": shield_option,
            "EXT_MOUNTED": mounted_option,
        },
    )

    assert len(army.entries) == 2

    first_entry = army.entries[0]
    second_entry = army.entries[1]

    assert first_entry.profile is profile
    assert second_entry.profile is profile

    assert (
        first_entry.configured_profile
        is not second_entry.configured_profile
    )

    assert (
        first_entry.configured_profile.selected_options
        == (shield_option,)
    )

    assert (
        second_entry.configured_profile.selected_options
        == (mounted_option,)
    )

    assert first_entry.total_points() == 25
    assert second_entry.total_points() == 30