"""DEV-077S-I2-G2-C4: production-profile shooting validation.

Uses actual canonical CSV relationships. No scoring changes.
Run from the project root with src on the normal pytest Python path.
"""
import pytest

from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState
from hero_hunting_shooting import calculate_hero_hunting_shooting_evidence
from hero_hunting_concentrated_fire import (
    FocusedShooter, calculate_concentrated_fire_evidence,
)
from lethal_aim_state import LethalAimSpend, LethalAimState
from loader import load_all_profiles
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_loader import load_profile_options
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from wargear_loader import load_wargear
from ranged_weapon_resolver import resolve_ranged_weapon
from shooting_eligibility import ShootingContext


@pytest.fixture(scope="module")
def production():
    profiles = {p.id: p for p in load_all_profiles()}
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_special_rules(
        profiles=profiles, special_rules=load_special_rules()
    )
    options = load_profile_options(profiles=profiles)
    load_profile_option_wargear_assignments(
        profile_options=options, wargear=wargear
    )
    return profiles, options


def shooter(profile, defender, *, distance=12, moved=False,
            spend=None, free_might=None):
    weapon = resolve_ranged_weapon(profile)
    assert weapon is not None
    return calculate_hero_hunting_shooting_evidence(
        attacker=profile, defender=defender, weapon=weapon,
        defender_state=DefensiveState(2, remaining_fate=1),
        context=ShootingContext(
            target_distance_inches=distance, moved_this_turn=moved
        ),
        clear_line_of_sight=True,
        lethal_aim_spend=spend,
        lethal_aim_state=free_might,
    )


def test_narzug_canonical_equipment_and_rules(production):
    profiles, _ = production
    narzug = ConfiguredProfile(profiles["NARZUG"])
    assert resolve_ranged_weapon(narzug).wargear_id == "WG_ORC_BOW"
    rule_ids = {a.rule.id for a in narzug.effective_special_rules}
    assert {"LETHAL_AIM", "EXPERT_SHOT", "POISONED_ATTACKS"} <= rule_ids


def test_narzug_multiple_shot_lethal_aim_fails_closed(production):
    profiles, _ = production
    narzug = ConfiguredProfile(profiles["NARZUG"])
    defender = ConfiguredProfile(profiles["BOLG_SPAWN_OF_AZOG"])
    with pytest.raises(ValueError, match="across multiple shots"):
        shooter(
            narzug, defender, spend=LethalAimSpend.TO_WOUND,
            free_might=LethalAimState()
        )


def test_narzug_without_explicit_allocation_fails_closed(production):
    profiles, _ = production
    with pytest.raises(ValueError, match="allocation must be explicit"):
        shooter(
            ConfiguredProfile(profiles["NARZUG"]),
            ConfiguredProfile(profiles["BOLG_SPAWN_OF_AZOG"]),
        )


def test_hunter_orc_bow_option_enables_target_specific_shooting(production):
    profiles, options = production
    hunter = ConfiguredProfile(
        profiles["DG_HOW"],
        selected_options=(options["DG_HOW_ORC_BOW_AH"],),
    )
    target = ConfiguredProfile(profiles["BOLG_SPAWN_OF_AZOG"])
    weapon = resolve_ranged_weapon(hunter)
    assert weapon.wargear_id == "WG_ORC_BOW"
    result = shooter(hunter, target)
    assert result.shots == 1
    assert 0 <= result.elimination_probability <= 1


def test_real_hunter_orcs_combine_fate_once(production):
    profiles, options = production
    hunter = ConfiguredProfile(
        profiles["DG_HOW"],
        selected_options=(options["DG_HOW_ORC_BOW_AH"],),
    )
    target = ConfiguredProfile(profiles["BOLG_SPAWN_OF_AZOG"])
    weapon = resolve_ranged_weapon(hunter)
    entries = tuple(
        FocusedShooter(
            shooter_id=f"hunter-{i}",
            attacker=hunter,
            weapon=weapon,
            context=ShootingContext(target_distance_inches=12),
            clear_line_of_sight=True,
        )
        for i in range(3)
    )
    result = calculate_concentrated_fire_evidence(
        shooters=entries, defender=target,
        defender_state=DefensiveState(2, remaining_fate=1),
    )
    assert result.total_shots == 3
    assert result.shooter_count == 3
    assert sum(result.incoming_wound_distribution) == 1
    assert 0 <= result.elimination_probability <= 1


def test_real_hunter_orc_out_of_range_rejected(production):
    profiles, options = production
    hunter = ConfiguredProfile(
        profiles["DG_HOW"],
        selected_options=(options["DG_HOW_ORC_BOW_AH"],),
    )
    with pytest.raises(ValueError, match="cannot fire"):
        shooter(
            hunter, ConfiguredProfile(profiles["BOLG_SPAWN_OF_AZOG"]),
            distance=19,
        )
