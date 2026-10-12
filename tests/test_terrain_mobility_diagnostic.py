"""DEV-077S-I2-D-B1 diagnostic regression tests."""
import pytest

from army import Army
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from fielded_model_form_state import FieldedModelFormState
from mount import Mount
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from terrain_mobility_diagnostic import calculate_terrain_mobility_diagnostic


def make_profile(*, movement=6, base_size_mm=25, mounted=False, hunt_master=False):
    profile = Profile(
        id="TEST_RIDER", name="Test Rider", points=20,
        movement=movement, base_size_mm=base_size_mm,
        fight=4, shooting="4+", strength=4, defence=5,
        attacks=2, wounds=2, courage="6+", intelligence="7+",
        might=2, will=1, fate=1, max_in_army=0,
    )
    if mounted:
        profile.default_mount = Mount(
            id="MOUNT_TEST", name="Test Mount", movement=10,
            fight=3, shooting="6+", strength=4, defence=4,
            attacks=1, wounds=1, courage="8+", intelligence="7+",
            base_size_mm=40,
        )
    if hunt_master:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="HUNT_MASTER", name="Hunt Master",
                             category=RuleCategory.SPECIAL)
        ))
    return ConfiguredProfile(profile=profile)


def army_with(profile, quantity=1):
    army = Army()
    army.add_configured_profile(profile, quantity=quantity)
    return army


def test_standard_infantry_has_half_terrain_manoeuvrability():
    result = calculate_terrain_mobility_diagnostic(army_with(make_profile()))
    assert result.open_ground == pytest.approx(6.0)
    assert result.difficult_terrain == pytest.approx(3.0)
    assert result.terrain_retention == pytest.approx(0.5)


def test_large_base_reduces_both_accessibility_scores():
    small = calculate_terrain_mobility_diagnostic(army_with(make_profile(base_size_mm=25)))
    large = calculate_terrain_mobility_diagnostic(army_with(make_profile(base_size_mm=80)))
    assert small.open_ground > large.open_ground
    assert small.difficult_terrain > large.difficult_terrain
    assert large.terrain_retention == pytest.approx(0.5)


def test_mounted_hunt_master_preserves_difficult_terrain_movement():
    ordinary = calculate_terrain_mobility_diagnostic(army_with(make_profile(mounted=True)))
    exempt = calculate_terrain_mobility_diagnostic(army_with(make_profile(mounted=True, hunt_master=True)))
    assert exempt.open_ground == pytest.approx(ordinary.open_ground)
    assert exempt.difficult_terrain == pytest.approx(exempt.open_ground)
    assert ordinary.terrain_retention == pytest.approx(0.5)
    assert exempt.terrain_retention == pytest.approx(1.0)


def test_hunt_master_does_not_exempt_unmounted_infantry():
    result = calculate_terrain_mobility_diagnostic(army_with(make_profile(hunt_master=True)))
    assert result.terrain_retention == pytest.approx(0.5)


def test_quantity_weighted_model_average():
    army = Army()
    army.add_configured_profile(make_profile(movement=6), quantity=3)
    army.add_configured_profile(make_profile(movement=10), quantity=1)
    result = calculate_terrain_mobility_diagnostic(army)
    assert result.model_count == 4
    assert result.open_ground == pytest.approx(7.0)
    assert result.difficult_terrain == pytest.approx(3.5)


def test_runtime_dismount_changes_movement_and_base_size():
    configured = make_profile(mounted=True, hunt_master=True)
    army = army_with(configured)
    model = army.fielded_models()[0]
    mounted = FieldedModelFormState(
        fielded_model=model, active_configured_profile=configured, mount_active=True
    )
    dismounted = FieldedModelFormState(
        fielded_model=model, active_configured_profile=configured, mount_active=False
    )
    a = calculate_terrain_mobility_diagnostic(army, form_states=(mounted,))
    b = calculate_terrain_mobility_diagnostic(army, form_states=(dismounted,))
    assert a.open_ground > b.open_ground
    assert a.terrain_retention == pytest.approx(1.0)
    assert b.terrain_retention == pytest.approx(0.5)


def test_form_states_must_cover_all_fielded_models():
    army = army_with(make_profile(), quantity=2)
    with pytest.raises(ValueError, match="exactly one state"):
        calculate_terrain_mobility_diagnostic(army, form_states=())


def test_empty_army_has_zero_diagnostic():
    result = calculate_terrain_mobility_diagnostic(Army())
    assert result.model_count == 0
    assert result.open_ground == result.difficult_terrain == result.terrain_retention == 0.0
