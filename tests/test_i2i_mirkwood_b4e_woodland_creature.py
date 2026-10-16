"""DEV-077S-I2-I-C3-D7-B4-B4-E: explicit woodland movement checks."""
import pytest
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from terrain_movement import (
    get_effective_movement_in_terrain,
    ignores_difficult_terrain_movement_penalty,
    terrain_traversal_capabilities,
)

def combatant(rule=None):
    p = Profile(id="MW_TEST", name="Elf", points=14, movement=6,
        fight=5, shooting="3+", strength=3, defence=3, attacks=1,
        wounds=1, courage="5+", intelligence="6+", might=0, will=0,
        fate=0, max_in_army=0)
    if rule:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule, name=rule, category=RuleCategory.MOVEMENT)))
    return ConfiguredProfile(profile=p)

def test_woodland_creature_keeps_full_move_through_woods():
    assert get_effective_movement_in_terrain(combatant("WOODLAND_CREATURE"), in_difficult_terrain=True, is_woodland=True) == 6

def test_without_rule_woodland_still_halves_move():
    assert get_effective_movement_in_terrain(combatant(), in_difficult_terrain=True, is_woodland=True) == 3

@pytest.mark.parametrize("kind", [{}, {"is_water_feature":True}])
def test_woodland_creature_does_not_bypass_other_difficult_terrain(kind):
    assert get_effective_movement_in_terrain(combatant("WOODLAND_CREATURE"), in_difficult_terrain=True, **kind) == 3

def test_open_ground_unchanged():
    assert get_effective_movement_in_terrain(combatant("WOODLAND_CREATURE")) == 6

def test_does_not_grant_global_difficult_terrain_exemption():
    caps=terrain_traversal_capabilities(combatant("WOODLAND_CREATURE"))
    assert caps.ignore_non_water_difficult_terrain is False
    assert caps.ignore_water_difficult_terrain is False

def test_explicit_woodland_flag_controls_exemption():
    ranger=combatant("WOODLAND_CREATURE")
    assert ignores_difficult_terrain_movement_penalty(ranger, is_woodland=True)
    assert not ignores_difficult_terrain_movement_penalty(ranger)

@pytest.mark.parametrize("call", [get_effective_movement_in_terrain, ignores_difficult_terrain_movement_penalty])
def test_contradictory_terrain_classification_rejected(call):
    with pytest.raises(ValueError):
        call(combatant("WOODLAND_CREATURE"), is_water_feature=True, is_woodland=True)

def test_existing_spectral_walk_non_water_exemption():
    assert get_effective_movement_in_terrain(combatant("SPECTRAL_WALK"),in_difficult_terrain=True)==6

def test_existing_swift_movement_non_water_exemption():
    assert get_effective_movement_in_terrain(combatant("SWIFT_MOVEMENT"),in_difficult_terrain=True)==6

def test_profile_statline_unchanged():
    ranger=combatant("WOODLAND_CREATURE")
    get_effective_movement_in_terrain(ranger,in_difficult_terrain=True,is_woodland=True)
    assert ranger.profile.movement==6
