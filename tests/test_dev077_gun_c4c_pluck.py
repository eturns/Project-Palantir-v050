from types import SimpleNamespace

import pytest

from gundabad_pluck import (
    PluckStatus,
    PluckTarget,
    pluck_opportunity,
)
from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules


def bat():
    profiles = {profile.id: profile for profile in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    return ConfiguredProfile(profiles["WAR_BAT"])


def opportunity(attacker=None, crossed=None, **overrides):
    arguments = dict(
        charged_into_combat=True,
        flew_during_move=True,
        legal_flight_charge=True,
        crossed_enemy_models=(PluckTarget("enemy1", 25),) if crossed is None else crossed,
    )
    arguments.update(overrides)
    return pluck_opportunity(bat() if attacker is None else attacker, **arguments)


def test_real_war_bat_has_fly_and_pluck():
    ids = {assignment.rule.id for assignment in bat().effective_special_rules}
    assert {"FLY", "PLUCK"} <= ids


def test_one_eligible_target_has_exact_four_plus_roll():
    result = opportunity()
    assert result.status is PluckStatus.READY
    assert result.eligible_target_ids == ("enemy1",)
    assert [result.resolve(chosen_target_id="enemy1", natural_roll=i) for i in range(1, 7)] == [
        False, False, False, True, True, True
    ]


def test_only_25mm_crossed_enemies_eligible():
    result = opportunity(crossed=(PluckTarget("small", 25), PluckTarget("large", 40)))
    assert result.eligible_target_ids == ("small",)
    with pytest.raises(ValueError, match="eligible"):
        result.resolve(chosen_target_id="large", natural_roll=6)


def test_no_25mm_target_is_distinct_from_illegal_activation():
    result = opportunity(crossed=(PluckTarget("large", 40),))
    assert result.status is PluckStatus.NO_TARGET
    with pytest.raises(ValueError, match="No legal"):
        result.resolve(chosen_target_id="large", natural_roll=6)


@pytest.mark.parametrize("change", [
    {"charged_into_combat": False},
    {"flew_during_move": False},
    {"legal_flight_charge": False},
])
def test_no_pluck_without_flying_legal_charge(change):
    assert opportunity(**change).status is PluckStatus.INELIGIBLE


def test_non_bat_does_not_gain_pluck():
    other = SimpleNamespace(profile=SimpleNamespace(id="GUNDABAD_OGRE"), effective_special_rules=())
    assert opportunity(attacker=other).status is PluckStatus.INELIGIBLE


def test_multiple_eligible_enemies_permit_one_chosen_target():
    result = opportunity(crossed=(PluckTarget("a", 25), PluckTarget("b", 25)))
    assert result.eligible_target_ids == ("a", "b")
    assert result.resolve(chosen_target_id="b", natural_roll=4)


def test_invalid_roll_and_duplicate_contacts_rejected():
    result = opportunity()
    for value in (0, 7, True, 3.1):
        with pytest.raises(ValueError, match="D6"):
            result.resolve(chosen_target_id="enemy1", natural_roll=value)
    with pytest.raises(ValueError, match="Duplicate"):
        opportunity(crossed=(PluckTarget("same", 25), PluckTarget("same", 25)))
