"""DEV-077S-I2-D-B4a: confirmed terrain rules from MESBG Rules Manual (2024)."""
import pytest

from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profiles import Profile
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule
from terrain_movement import (
    get_effective_movement_in_terrain,
    ignores_difficult_terrain_movement_penalty,
    terrain_traversal_capabilities,
)
from army import Army
from terrain_mobility_diagnostic import calculate_terrain_mobility_diagnostic


def profile_with_rules(*rule_ids, base_size_mm=25):
    p = Profile(
        id="GENERIC", name="Generic", points=20, movement=6,
        base_size_mm=base_size_mm, fight=3, shooting="4+", strength=3,
        defence=4, attacks=1, wounds=1, courage="6+", intelligence="7+",
        might=0, will=0, fate=0, max_in_army=0,
    )
    for rule_id in rule_ids:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule_id, name=rule_id, category=RuleCategory.MOVEMENT)
        ))
    return ConfiguredProfile(profile=p)


def test_spectral_walk_ignores_land_and_water_slowdown():
    model = profile_with_rules("SPECTRAL_WALK")
    assert get_effective_movement_in_terrain(model, in_difficult_terrain=True) == 6
    assert get_effective_movement_in_terrain(model, in_difficult_terrain=True, is_water_feature=True) == 6


def test_spectral_walk_has_automatic_traversal_results_not_swift_obstacle_bypass():
    capabilities = terrain_traversal_capabilities(profile_with_rules("SPECTRAL_WALK"))
    assert capabilities.automatic_climb_jump_leap_swim_six
    assert not capabilities.ignore_obstacles_without_climb_or_jump_test


def test_swift_movement_ignores_land_but_not_water_slowdown():
    model = profile_with_rules("SWIFT_MOVEMENT")
    assert get_effective_movement_in_terrain(model, in_difficult_terrain=True) == 6
    assert get_effective_movement_in_terrain(model, in_difficult_terrain=True, is_water_feature=True) == 3


def test_swift_movement_bypasses_obstacle_tests_but_tracks_vertical_distance():
    caps = terrain_traversal_capabilities(profile_with_rules("SWIFT_MOVEMENT"))
    assert caps.ignore_obstacles_without_climb_or_jump_test
    assert caps.vertical_distance_counts_toward_move
    assert not caps.automatic_climb_jump_leap_swim_six


def test_ordinary_infantry_retains_normal_difficult_terrain_penalties():
    model = profile_with_rules()
    assert not ignores_difficult_terrain_movement_penalty(model)
    assert not ignores_difficult_terrain_movement_penalty(model, is_water_feature=True)
    assert get_effective_movement_in_terrain(model, in_difficult_terrain=True) == 3


def test_swift_and_spectral_do_not_remove_large_base_accessibility_penalty():
    small = Army()
    large = Army()
    small.add_configured_profile(profile_with_rules("SWIFT_MOVEMENT", base_size_mm=25))
    large.add_configured_profile(profile_with_rules("SWIFT_MOVEMENT", base_size_mm=60))
    a = calculate_terrain_mobility_diagnostic(small)
    b = calculate_terrain_mobility_diagnostic(large)
    assert a.open_ground > b.open_ground
    assert a.difficult_terrain > b.difficult_terrain
    assert a.terrain_retention == pytest.approx(1)
    assert b.terrain_retention == pytest.approx(1)


def test_swift_and_spectral_rule_combination_keeps_water_exemption():
    model = profile_with_rules("SWIFT_MOVEMENT", "SPECTRAL_WALK")
    assert get_effective_movement_in_terrain(model, in_difficult_terrain=True, is_water_feature=True) == 6
