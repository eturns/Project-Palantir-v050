import pytest

from army import Army
from army_manoeuvrability import (
    calculate_army_manoeuvrability,
)
from profiles import Profile
from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from special_rule import SpecialRule
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from database.rule_category import RuleCategory
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from profile_option import ProfileOption

def make_profile(
    *,
    profile_id: str,
    movement: float,
    base_size_mm: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=movement,
        fight=3,
        shooting="4+",
        strength=3,
        defence=3,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        base_size_mm=base_size_mm,
    )


def test_army_manoeuvrability_is_quantity_weighted_average():
    army = Army()

    army.add_profile(
        make_profile(
            profile_id="FAST",
            movement=10,
            base_size_mm=40,
        ),
        quantity=1,
    )

    army.add_profile(
        make_profile(
            profile_id="STANDARD",
            movement=6,
            base_size_mm=25,
        ),
        quantity=3,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    expected = (
        7.905694150420948
        + (6.0 * 3)
    ) / 4

    assert result == pytest.approx(expected)

def test_army_manoeuvrability_includes_profile_mobility_rule_score():
    army = Army()

    profile = make_profile(
        profile_id="MOBILE",
        movement=6,
        base_size_mm=25,
    )

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )
    
    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )
    
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=unnatural_speed,
        )
    )

    army.add_profile(
        profile,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    assert result > 6.0

def test_army_manoeuvrability_weights_mobility_rules_by_model_quantity():
    army = Army()

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )

    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    mobile_profile = make_profile(
        profile_id="MOBILE",
        movement=6,
        base_size_mm=25,
    )

    mobile_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=unnatural_speed,
        )
    )

    standard_profile = make_profile(
        profile_id="STANDARD",
        movement=6,
        base_size_mm=25,
    )

    army.add_profile(
        mobile_profile,
        quantity=1,
    )

    army.add_profile(
        standard_profile,
        quantity=3,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    expected = (
        7.5
        + (6.0 * 3)
    ) / 4

    assert result == pytest.approx(
        expected,
    )

def test_spiritual_displacement_gives_no_mobility_bonus_with_one_abyssal_knight():
    army = Army()

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    spiritual_displacement = SpecialRule(
        id="SPIRITUAL_DISPLACEMENT",
        name="Spiritual Displacement",
        category=RuleCategory.MOBILITY,
    )

    spiritual_displacement.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    abyssal_knight = make_profile(
        profile_id="DG_AK",
        movement=6,
        base_size_mm=25,
    )

    abyssal_knight.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=spiritual_displacement,
        )
    )

    army.add_profile(
        abyssal_knight,
        quantity=1,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    assert result == pytest.approx(
        6.0,
    )

def test_spiritual_displacement_gives_one_mobility_bonus_with_two_abyssal_knights():
    army = Army()

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    spiritual_displacement = SpecialRule(
        id="SPIRITUAL_DISPLACEMENT",
        name="Spiritual Displacement",
        category=RuleCategory.MOBILITY,
    )

    spiritual_displacement.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    abyssal_knight = make_profile(
        profile_id="DG_AK",
        movement=6,
        base_size_mm=25,
    )

    abyssal_knight.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=spiritual_displacement,
        )
    )

    army.add_profile(
        abyssal_knight,
        quantity=2,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    expected = (
        6.0
        + 6.0
        + 1.5
    ) / 2

    assert result == pytest.approx(
        expected,
    )

def test_spiritual_displacement_combines_with_other_profile_mobility_bonus():
    army = Army()

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    spiritual_displacement = SpecialRule(
        id="SPIRITUAL_DISPLACEMENT",
        name="Spiritual Displacement",
        category=RuleCategory.MOBILITY,
    )

    spiritual_displacement.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )

    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    abyssal_knight = make_profile(
        profile_id="DG_AK",
        movement=6,
        base_size_mm=25,
    )

    abyssal_knight.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=spiritual_displacement,
        )
    )

    lingering_shadow = make_profile(
        profile_id="DG_LS",
        movement=6,
        base_size_mm=25,
    )

    lingering_shadow.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=unnatural_speed,
        )
    )

    army.add_profile(
        abyssal_knight,
        quantity=2,
    )

    army.add_profile(
        lingering_shadow,
        quantity=1,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    expected = (
        6.0
        + 6.0
        + 7.5
        + 1.5
    ) / 3

    assert result == pytest.approx(
        expected,
    )

def test_single_slayer_of_men_has_no_pairing_mobility_penalty():
    army = Army()

    slayer = make_profile(
        profile_id="DG_SM",
        movement=6,
        base_size_mm=25,
    )

    army.add_profile(
        slayer,
        quantity=1,
    )

    angmar_arise = SpecialRule(
        id="ANGMAR_ARISE_SOM",
        name="Angmar Arise",
        category=RuleCategory.OFFENCE,
    )

    slayer.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=angmar_arise,
        )
    )
    result = calculate_army_manoeuvrability(
        army,
    )

    assert result == pytest.approx(
        6.0,
    )


def test_two_slayers_of_men_have_pairing_mobility_cost():
    army = Army()

    slayer = make_profile(
        profile_id="DG_SM",
        movement=6,
        base_size_mm=25,
    )

    army.add_profile(
        slayer,
        quantity=2,
    )

    angmar_arise = SpecialRule(
        id="ANGMAR_ARISE_SOM",
        name="Angmar Arise",
        category=RuleCategory.OFFENCE,
    )

    slayer.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=angmar_arise,
        )
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    assert result == pytest.approx(
        5.875,
    )

def test_spiritual_displacement_does_not_suppress_other_mobility_on_same_profile():
    army = Army()

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    spiritual_displacement = SpecialRule(
        id="SPIRITUAL_DISPLACEMENT",
        name="Spiritual Displacement",
        category=RuleCategory.MOBILITY,
    )

    spiritual_displacement.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )

    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.25,
        )
    )

    abyssal_knight = make_profile(
        profile_id="DG_AK",
        movement=6,
        base_size_mm=25,
    )

    abyssal_knight.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=spiritual_displacement,
        )
    )

    abyssal_knight.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=unnatural_speed,
        )
    )

    army.add_profile(
        abyssal_knight,
        quantity=1,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    assert result == pytest.approx(
        7.25,
    )

def test_configured_movement_changes_army_manoeuvrability():
    profile = make_profile(
        profile_id="MOUNTABLE",
        movement=6,
        base_size_mm=25,
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

    profile.profile_options.append(
        mounted_option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    mounted = ConfiguredProfile(
        profile=profile,
        selected_options=(
            mounted_option,
        ),
    )

    plain_army = Army()
    plain_army.add_configured_profile(
        plain,
    )

    mounted_army = Army()
    mounted_army.add_configured_profile(
        mounted,
    )

    plain_result = calculate_army_manoeuvrability(
        plain_army,
    )

    mounted_result = calculate_army_manoeuvrability(
        mounted_army,
    )

    assert plain_result == pytest.approx(
        6.0,
    )

    assert mounted_result > plain_result

def test_configured_base_size_changes_army_manoeuvrability():
    profile = make_profile(
        profile_id="LARGE_BASE",
        movement=6,
        base_size_mm=25,
    )

    large_base_option = ProfileOption(
        id="LARGE_BASE_OPTION",
        name="Large Base",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                base_size_override_mm=40,
            ),
        ),
    )

    profile.profile_options.append(
        large_base_option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    large_base = ConfiguredProfile(
        profile=profile,
        selected_options=(
            large_base_option,
        ),
    )

    plain_army = Army()
    plain_army.add_configured_profile(
        plain,
    )

    large_base_army = Army()
    large_base_army.add_configured_profile(
        large_base,
    )

    plain_result = calculate_army_manoeuvrability(
        plain_army,
    )

    large_base_result = calculate_army_manoeuvrability(
        large_base_army,
    )

    assert large_base_result != pytest.approx(
        plain_result,
    )

def test_configured_added_mobility_rule_changes_manoeuvrability():
    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )

    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    assignment = ProfileSpecialRuleAssignment(
        rule=unnatural_speed,
    )

    profile = make_profile(
        profile_id="CONFIGURED_MOBILE",
        movement=6,
        base_size_mm=25,
    )

    option = ProfileOption(
        id="MOBILITY_OPTION",
        name="Mobility Option",
        points=5,
        configured_state_effects=(
            ConfiguredStateEffect(
                granted_special_rules=(
                    assignment,
                ),
            ),
        ),
    )

    profile.profile_options.append(
        option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    mobile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    plain_army = Army()
    plain_army.add_configured_profile(
        plain,
    )

    mobile_army = Army()
    mobile_army.add_configured_profile(
        mobile,
    )

    assert calculate_army_manoeuvrability(
        plain_army,
    ) == pytest.approx(
        6.0,
    )

    assert calculate_army_manoeuvrability(
        mobile_army,
    ) == pytest.approx(
        7.5,
    )

def test_configured_removed_mobility_rule_stops_contributing():
    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )

    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    assignment = ProfileSpecialRuleAssignment(
        rule=unnatural_speed,
    )

    profile = make_profile(
        profile_id="BASE_MOBILE",
        movement=6,
        base_size_mm=25,
    )

    profile.special_rules.append(
        assignment,
    )

    option = ProfileOption(
        id="REMOVE_MOBILITY",
        name="Remove Mobility",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                removed_special_rule_ids=(
                    "UNNATURAL_SPEED",
                ),
            ),
        ),
    )

    profile.profile_options.append(
        option,
    )

    configured = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    army = Army()
    army.add_configured_profile(
        configured,
    )

    assert calculate_army_manoeuvrability(
        army,
    ) == pytest.approx(
        6.0,
    )

def test_same_profile_with_two_configurations_remains_distinct_in_manoeuvrability():
    profile = make_profile(
        profile_id="GENERIC_HERO",
        movement=6,
        base_size_mm=25,
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

    profile.profile_options.append(
        mounted_option,
    )

    plain = ConfiguredProfile(
        profile=profile,
    )

    mounted = ConfiguredProfile(
        profile=profile,
        selected_options=(
            mounted_option,
        ),
    )

    army = Army()

    army.add_configured_profile(
        plain,
    )

    army.add_configured_profile(
        mounted,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    assert len(army.entries) == 2
    assert (
        army.entries[0].profile
        is army.entries[1].profile
    )

    assert result > 6.0