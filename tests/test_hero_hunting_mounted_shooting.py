"""DEV-077S-I2-G2-C5C: real mounted-shooter integration contract.

Diagnostic-only: no dashboard or scoring changes. Tests use canonical
profile/option/mount/wargear data and the accepted C1 shooting pathway.
"""
import pytest
from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState
from hero_hunting_shooting import calculate_hero_hunting_shooting_evidence
from loader import load_all_profiles
from mount_loader import load_mounts
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_loader import load_profile_options
from profile_option_mount_loader import load_profile_option_mount_assignments
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from wargear_loader import load_wargear
from ranged_weapon_resolver import resolve_ranged_weapon
from shooting_eligibility import ShootingContext
from shooting_to_hit_modifier import get_movement_shooting_modifier


@pytest.fixture(scope="module")
def real_data():
    profiles = {p.id: p for p in load_all_profiles()}
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    options = load_profile_options(profiles=profiles)
    load_profile_option_wargear_assignments(profile_options=options, wargear=wargear)
    load_profile_option_mount_assignments(profile_options=options, mounts=load_mounts())
    return profiles, options


def _mounted_captain(real_data):
    profiles, options = real_data
    captain = ConfiguredProfile(
        profiles["DG_HOC"],
        selected_options=(
            options["DG_HOC_FELL_WARG_AH"],
            options["DG_HOC_ORC_BOW_AH"],
        ),
    )
    target = ConfiguredProfile(profiles["DG_HOW"])
    return captain, target


def _shoot(attacker, defender, *, moved=False, distance=12, engaged=False):
    weapon = resolve_ranged_weapon(attacker)
    return calculate_hero_hunting_shooting_evidence(
        attacker=attacker, defender=defender, weapon=weapon,
        defender_state=DefensiveState(1),
        context=ShootingContext(
            moved_this_turn=moved,
            engaged_in_combat=engaged,
            target_distance_inches=distance,
        ),
        clear_line_of_sight=True,
    )


def test_fell_warg_and_orc_bow_both_load_from_real_options(real_data):
    captain, _ = _mounted_captain(real_data)
    assert captain.effective_mount is not None
    assert captain.effective_mount.id == "MOUNT_FELL_WARG"
    assert resolve_ranged_weapon(captain).wargear_id == "WG_ORC_BOW"


def test_mounted_captain_uses_rider_shoot_value_not_mount_value(real_data):
    captain, _ = _mounted_captain(real_data)
    assert captain.effective_shooting == captain.profile.shooting


def test_moving_mounted_archer_has_standard_to_hit_penalty(real_data):
    captain, defender = _mounted_captain(real_data)
    stationary = _shoot(captain, defender)
    moving = _shoot(captain, defender, moved=True)
    assert get_movement_shooting_modifier(captain, moved_this_turn=True) == -1
    assert moving.wound_probability_per_shot < stationary.wound_probability_per_shot


def test_mount_does_not_remove_bow_or_add_shots(real_data):
    captain, defender = _mounted_captain(real_data)
    result = _shoot(captain, defender)
    assert result.shots == 1
    assert result.wound_probability_per_shot > 0


def test_mounted_shooter_out_of_range_rejected(real_data):
    captain, defender = _mounted_captain(real_data)
    with pytest.raises(ValueError, match="cannot fire"):
        _shoot(captain, defender, distance=19)


def test_mounted_shooter_engaged_cannot_fire_without_exception(real_data):
    captain, defender = _mounted_captain(real_data)
    with pytest.raises(ValueError, match="cannot fire"):
        _shoot(captain, defender, engaged=True)


def test_mount_without_bow_is_not_ranged_shooter(real_data):
    profiles, options = real_data
    captain = ConfiguredProfile(
        profiles["DG_HOC"],
        selected_options=(options["DG_HOC_FELL_WARG_AH"],),
    )
    assert captain.effective_mount is not None
    assert resolve_ranged_weapon(captain) is None


def test_on_foot_and_mounted_bow_options_share_weapon_profile(real_data):
    profiles, options = real_data
    on_foot = ConfiguredProfile(
        profiles["DG_HOC"],
        selected_options=(options["DG_HOC_ORC_BOW_AH"],),
    )
    mounted, _ = _mounted_captain(real_data)
    assert resolve_ranged_weapon(on_foot) == resolve_ranged_weapon(mounted)
