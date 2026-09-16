from configured_profile import (
    ConfiguredProfile,
    create_configured_profile_from_external_options,
)
from profile_option import ProfileOption
from profiles import Profile
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from wargear import Wargear
from configured_state_effect import ConfiguredStateEffect
from profile_classification import ModelType

from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule
from mount import Mount
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from configured_state_effect import ConfiguredStateEffect
from profile_classification import (
    HeroicStatus,
    ModelType,
)
from profile_option import ProfileOption

def create_test_profile(
    profile_id: str = "IH_WR",
    points: int = 10,
) -> Profile:
    return Profile(
        id=profile_id,
        name="Iron Hills Warrior",
        points=points,
        movement=5,
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


def test_configured_profile_without_options_uses_base_points():
    profile = create_test_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.points == 10


def test_configured_profile_adds_selected_option_points():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
    )
    profile.profile_options.append(shield_and_spear)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(shield_and_spear,),
    )

    assert configured_profile.points == 12


def test_configured_profile_adds_multiple_option_points():
    profile = create_test_profile(points=80)

    first_option = ProfileOption(
        id="FIRST_OPTION",
        name="First option",
        points=25,
    )

    second_option = ProfileOption(
        id="SECOND_OPTION",
        name="Second option",
        points=5,
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    assert configured_profile.points == 110


def test_configured_profile_allows_free_option():
    profile = create_test_profile(points=80)

    mattock_exchange = ProfileOption(
        id="IH_CAP_MATTOCK",
        name="Exchange shield and spear for Mattock",
        points=0,
        external_id="OPT0720",
    )

    profile.profile_options.append(mattock_exchange)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(mattock_exchange,),
    )

    assert configured_profile.points == 80


def test_configured_profile_preserves_canonical_profile():
    profile = create_test_profile()

    option = ProfileOption(
        id="IH_WR_CROSSBOW",
        name="Crossbow",
        points=2,
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.profile is profile
    assert profile.points == 10

def test_configured_profile_accepts_legal_selected_option():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    profile.profile_options.append(shield_and_spear)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(shield_and_spear,),
    )

    assert configured_profile.selected_options == (
        shield_and_spear,
    )


def test_configured_profile_rejects_illegal_selected_option():
    profile = create_test_profile()

    crossbow = ProfileOption(
        id="IH_WR_CROSSBOW",
        name="Crossbow",
        points=2,
    )

    try:
        ConfiguredProfile(
            profile=profile,
            selected_options=(crossbow,),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an option "
            "that is not legal for the Profile."
        )

def test_effective_wargear_uses_profile_default_wargear():
    profile = create_test_profile()

    heavy_armour = Wargear(
        id="WG_HEAVY_ARMOUR",
        name="Heavy armour",
    )

    hand_weapon = Wargear(
        id="WG_HAND_WEAPON",
        name="Hand weapon",
    )

    profile.default_wargear.extend(
        (
            heavy_armour,
            hand_weapon,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_wargear == (
        heavy_armour,
        hand_weapon,
    )


def test_effective_wargear_applies_granted_wargear():
    profile = create_test_profile()

    heavy_armour = Wargear(
        id="WG_HEAVY_ARMOUR",
        name="Heavy armour",
    )

    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    profile.default_wargear.append(heavy_armour)

    option = ProfileOption(
        id="IH_WR_SHIELD",
        name="Shield",
        points=1,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_wargear == (
        heavy_armour,
        shield,
    )


def test_effective_wargear_applies_removed_wargear():
    profile = create_test_profile()

    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    spear = Wargear(
        id="WG_SPEAR",
        name="Spear",
    )

    mattock = Wargear(
        id="WG_MATTOCK",
        name="Mattock",
    )

    profile.default_wargear.extend(
        (
            shield,
            spear,
        )
    )

    option = ProfileOption(
        id="IH_CAP_MATTOCK",
        name="Exchange shield and spear for Mattock",
        points=0,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.REMOVE,
            ),
            ProfileOptionWargearAssignment(
                wargear=spear,
                action=WargearAssignmentAction.REMOVE,
            ),
            ProfileOptionWargearAssignment(
                wargear=mattock,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )

    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_wargear == (
        mattock,
    )


def test_effective_wargear_does_not_mutate_profile_defaults():
    profile = create_test_profile()

    shield = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    option = ProfileOption(
        id="REMOVE_SHIELD",
        name="Remove shield",
        points=0,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=shield,
                action=WargearAssignmentAction.REMOVE,
            ),
        ),
    )

    profile.default_wargear.append(shield)
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_wargear == ()
    assert profile.default_wargear == [shield]

def test_configured_profile_rejects_duplicate_selected_option():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
    )

    profile.profile_options.append(shield_and_spear)

    try:
        ConfiguredProfile(
            profile=profile,
            selected_options=(
                shield_and_spear,
                shield_and_spear,
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when the same option "
            "is selected more than once."
        )


def test_configured_profile_accepts_distinct_selected_options():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_OPTION",
        name="First option",
        points=1,
    )

    second_option = ProfileOption(
        id="SECOND_OPTION",
        name="Second option",
        points=2,
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    assert configured_profile.selected_options == (
        first_option,
        second_option,
    )

def test_create_configured_profile_from_external_options():
    profile = create_test_profile()

    shield_and_spear = ProfileOption(
        id="IH_WR_SHIELD_SPEAR",
        name="Shield and spear",
        points=2,
        external_id="OPT0723",
    )

    profile.profile_options.append(shield_and_spear)

    configured_profile = (
        create_configured_profile_from_external_options(
            profile=profile,
            external_option_ids=("OPT0723",),
            profile_options_by_external_id={
                "OPT0723": shield_and_spear,
            },
        )
    )

    assert configured_profile.profile is profile
    assert configured_profile.selected_options == (
        shield_and_spear,
    )
    assert configured_profile.points == 12


def test_external_option_configuration_rejects_unknown_id():
    profile = create_test_profile()

    try:
        create_configured_profile_from_external_options(
            profile=profile,
            external_option_ids=("OPT9999",),
            profile_options_by_external_id={},
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "external Profile Option ID."
        )


def test_external_option_configuration_rejects_option_for_wrong_profile():
    profile = create_test_profile()

    other_option = ProfileOption(
        id="OTHER_PROFILE_OPTION",
        name="Other Profile option",
        points=2,
        external_id="OPT0001",
    )

    try:
        create_configured_profile_from_external_options(
            profile=profile,
            external_option_ids=("OPT0001",),
            profile_options_by_external_id={
                "OPT0001": other_option,
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when the external option "
            "is not legal for the Profile."
        )

def test_effective_movement_uses_base_profile_movement_without_effect():
    profile = create_test_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_movement == 5


def test_effective_movement_applies_selected_option_override():
    profile = create_test_profile()

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

    assert configured_profile.effective_movement == 10


def test_effective_movement_does_not_mutate_base_profile():
    profile = create_test_profile()

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

    assert configured_profile.effective_movement == 10
    assert profile.movement == 5

def test_effective_movement_rejects_multiple_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_MOVEMENT",
        name="First Movement override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=8,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_MOVEMENT",
        name="Second Movement override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_movement
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple "
            "Movement overrides."
        )

def test_effective_defence_uses_base_profile_defence_without_effect():
    profile = create_test_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_defence == 6


def test_effective_defence_applies_selected_option_modifier():
    profile = create_test_profile()

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=1,
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

    assert configured_profile.effective_defence == 7


def test_effective_defence_combines_multiple_modifiers():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_DEFENCE",
        name="First Defence modifier",
        points=1,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_DEFENCE",
        name="Second Defence modifier",
        points=1,
        configured_state_effects=(
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    assert configured_profile.effective_defence == 8


def test_effective_defence_does_not_mutate_base_profile():
    profile = create_test_profile()

    shield_option = ProfileOption(
        id="SHIELD",
        name="Shield",
        points=1,
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

    assert configured_profile.effective_defence == 7
    assert profile.defence == 6

def test_effective_model_types_uses_base_profile_types_without_effect():
    profile = create_test_profile()

    profile.model_types.add(
        ModelType.INFANTRY
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_model_types == {
        ModelType.INFANTRY
    }


def test_effective_model_types_applies_selected_option_override():
    profile = create_test_profile()

    profile.model_types.add(
        ModelType.INFANTRY
    )

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

    assert configured_profile.effective_model_types == {
        ModelType.CAVALRY
    }


def test_effective_model_types_does_not_mutate_base_profile():
    profile = create_test_profile()

    profile.model_types.add(
        ModelType.INFANTRY
    )

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

    assert configured_profile.effective_model_types == {
        ModelType.CAVALRY
    }

    assert profile.model_types == {
        ModelType.INFANTRY
    }


def test_effective_model_types_rejects_multiple_overrides():
    profile = create_test_profile()

    profile.model_types.add(
        ModelType.INFANTRY
    )

    first_option = ProfileOption(
        id="FIRST_TYPE",
        name="First type override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                model_type_override=ModelType.CAVALRY,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_TYPE",
        name="Second type override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                model_type_override=ModelType.MONSTER,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_model_types
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple "
            "model type overrides."
        )

def test_effective_shooting_uses_base_profile_shooting_without_effect():
    profile = create_test_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_shooting == profile.shooting


def test_effective_shooting_applies_selected_option_override():
    profile = create_test_profile()

    shooting_option = ProfileOption(
        id="SHOOTING_OPTION",
        name="Shooting option",
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

    assert configured_profile.effective_shooting == "3+"


def test_effective_shooting_does_not_mutate_base_profile():
    profile = create_test_profile()
    original_shooting = profile.shooting

    shooting_option = ProfileOption(
        id="SHOOTING_OPTION",
        name="Shooting option",
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

    assert configured_profile.effective_shooting == "3+"
    assert profile.shooting == original_shooting


def test_effective_shooting_rejects_multiple_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_SHOOTING",
        name="First shooting override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                shooting_override="4+",
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_SHOOTING",
        name="Second shooting override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                shooting_override="3+",
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_shooting
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple "
            "shooting overrides."
        )

def test_effective_special_rules_uses_base_profile_rules_without_effect():
    profile = create_test_profile()

    base_rule = SpecialRule(
        id="BASE_RULE",
        name="Base Rule",
        category=RuleCategory.SPECIAL,
    )

    base_assignment = ProfileSpecialRuleAssignment(
        rule=base_rule,
    )

    profile.special_rules.append(
        base_assignment
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert configured_profile.effective_special_rules == [
        base_assignment
    ]


def test_effective_special_rules_includes_rule_granted_by_selected_option():
    profile = create_test_profile()

    granted_rule = SpecialRule(
        id="GRANTED_RULE",
        name="Granted Rule",
        category=RuleCategory.SPECIAL,
    )

    granted_assignment = ProfileSpecialRuleAssignment(
        rule=granted_rule,
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


def test_effective_special_rules_preserves_base_and_granted_rules():
    profile = create_test_profile()

    base_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="BASE_RULE",
            name="Base Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    granted_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="GRANTED_RULE",
            name="Granted Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    profile.special_rules.append(
        base_assignment
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
        base_assignment,
        granted_assignment,
    ]


def test_effective_special_rules_does_not_mutate_base_profile():
    profile = create_test_profile()

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

    assert configured_profile.effective_special_rules == [
        granted_assignment
    ]

    assert profile.special_rules == []

def test_effective_special_rules_removes_base_rule_by_id():
    profile = create_test_profile()

    removed_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="REMOVED_RULE",
            name="Removed Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    retained_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="RETAINED_RULE",
            name="Retained Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    profile.special_rules.extend(
        (
            removed_assignment,
            retained_assignment,
        )
    )

    rule_option = ProfileOption(
        id="REMOVE_RULE_OPTION",
        name="Remove rule option",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                removed_special_rule_ids=(
                    "REMOVED_RULE",
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
        retained_assignment
    ]


def test_effective_special_rules_can_remove_and_grant_in_same_configuration():
    profile = create_test_profile()

    base_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="BASE_RULE",
            name="Base Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    replacement_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="REPLACEMENT_RULE",
            name="Replacement Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    profile.special_rules.append(
        base_assignment
    )

    rule_option = ProfileOption(
        id="REPLACE_RULE_OPTION",
        name="Replace rule option",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                removed_special_rule_ids=(
                    "BASE_RULE",
                ),
                granted_special_rules=(
                    replacement_assignment,
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
        replacement_assignment
    ]


def test_effective_special_rule_removal_does_not_mutate_base_profile():
    profile = create_test_profile()

    base_assignment = ProfileSpecialRuleAssignment(
        rule=SpecialRule(
            id="BASE_RULE",
            name="Base Rule",
            category=RuleCategory.SPECIAL,
        ),
    )

    profile.special_rules.append(
        base_assignment
    )

    rule_option = ProfileOption(
        id="REMOVE_RULE_OPTION",
        name="Remove rule option",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                removed_special_rule_ids=(
                    "BASE_RULE",
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

    assert configured_profile.effective_special_rules == []
    assert profile.special_rules == [
        base_assignment
    ]

def test_effective_base_size_applies_selected_option_override():
    profile = create_test_profile()

    base_size_option = ProfileOption(
        id="LARGE_BASE",
        name="Large base",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    profile.profile_options.append(
        base_size_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            base_size_option,
        ),
    )

    assert configured_profile.effective_base_size_mm == 40


def test_effective_base_size_override_takes_precedence_over_mount():
    profile = create_test_profile()

    base_size_option = ProfileOption(
        id="BASE_OVERRIDE",
        name="Base override",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=50,
            ),
        ),
    )

    profile.profile_options.append(
        base_size_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            base_size_option,
        ),
    )

    assert configured_profile.effective_base_size_mm == 50


def test_effective_base_size_override_does_not_mutate_profile():
    profile = create_test_profile()
    original_base_size = profile.base_size_mm

    base_size_option = ProfileOption(
        id="LARGE_BASE",
        name="Large base",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    profile.profile_options.append(
        base_size_option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            base_size_option,
        ),
    )

    assert configured_profile.effective_base_size_mm == 40
    assert profile.base_size_mm == original_base_size


def test_effective_base_size_rejects_multiple_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_BASE",
        name="First base override",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_BASE",
        name="Second base override",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=50,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_base_size_mm
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple "
            "base-size overrides."
        )

def test_effective_base_size_override_takes_precedence_over_selected_mount():
    profile = create_test_profile()

    mount = Mount(
        id="TEST_MOUNT",
        name="Test Mount",
        base_size_mm=40,
    )

    mounted_option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=mount,
            ),
        ),
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=50,
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

    assert configured_profile.effective_mount is mount
    assert configured_profile.effective_mount.base_size_mm == 40
    assert configured_profile.effective_base_size_mm == 50

def test_effective_movement_rejects_duplicate_identical_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_MOVEMENT",
        name="First Movement override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_MOVEMENT",
        name="Second Movement override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                movement_override=10,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_movement
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "Movement overrides."
        )

def test_effective_model_types_rejects_duplicate_identical_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_TYPE",
        name="First type override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                model_type_override=ModelType.CAVALRY,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_TYPE",
        name="Second type override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                model_type_override=ModelType.CAVALRY,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_model_types
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "model type overrides."
        )


def test_effective_shooting_rejects_duplicate_identical_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_SHOOTING",
        name="First shooting override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                shooting_override="3+",
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_SHOOTING",
        name="Second shooting override",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                shooting_override="3+",
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_shooting
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "shooting overrides."
        )


def test_effective_base_size_rejects_duplicate_identical_overrides():
    profile = create_test_profile()

    first_option = ProfileOption(
        id="FIRST_BASE",
        name="First base override",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    second_option = ProfileOption(
        id="SECOND_BASE",
        name="Second base override",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    profile.profile_options.extend(
        (
            first_option,
            second_option,
        )
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_base_size_mm
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "base-size overrides."
        )

def test_configured_profile_can_override_heroic_status_and_resources():
    profile = create_test_profile(
        profile_id="IH_SIEGE_CREW",
    )
    profile.name = "Iron Hills Siege Crew"

    profile.heroic_status = HeroicStatus.WARRIOR
    profile.might = 0
    profile.will = 0
    profile.fate = 0

    effect = ConfiguredStateEffect(
        heroic_status_override=HeroicStatus.HERO,
        might_override=1,
        will_override=1,
        fate_override=1,
    )

    option = ProfileOption(
        id="SIEGE_VETERAN",
        name="Siege Veteran",
        points=0,
        configured_state_effects=(effect,),
    )

    profile.profile_options.append(option)

    configured = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured.effective_heroic_status is HeroicStatus.HERO
    assert configured.effective_might == 1
    assert configured.effective_will == 1
    assert configured.effective_fate == 1