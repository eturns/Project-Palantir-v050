from types import SimpleNamespace
import pytest

from flying_movement import (
    FlightMode, FlightLanding, has_fly, flight_movement,
    validate_flight_landing,
)
from terrain_movement import get_effective_movement_in_terrain
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from configured_profile import ConfiguredProfile


def _flying(movement=12):
    return SimpleNamespace(
        effective_movement=movement,
        effective_special_rules=(SimpleNamespace(rule=SimpleNamespace(id="FLY")),),
    )


def _landing(**kwargs):
    values = dict(overlaps_model=False, in_woodland=False, stable_surface=True,
                  enemy_reachable_surface=True, bridges_passage_underneath=False,
                  enemy_control_zone=False)
    values.update(kwargs)
    return FlightLanding(**values)


def test_generic_not_profile_specific():
    assert has_fly(_flying(10))
    assert flight_movement(_flying(10), FlightMode.FLY).distance_inches == 10
    assert not has_fly(SimpleNamespace(effective_special_rules=()))


def test_flying_ignores_intervening_terrain_and_vertical_distance():
    result = flight_movement(_flying(), FlightMode.FLY)
    assert result.ignores_intervening_models_and_terrain
    assert result.ignores_vertical_distance
    assert result.ignores_enemy_control_zones_en_route
    assert not result.may_enter_woodland


def test_ground_movement_is_four_and_does_not_ignore_terrain():
    result = flight_movement(_flying(), FlightMode.GROUND)
    assert result.distance_inches == 4
    assert not result.ignores_intervening_models_and_terrain
    assert result.may_enter_woodland


def test_terrain_movement_integration():
    flyer = _flying()
    assert get_effective_movement_in_terrain(flyer, in_difficult_terrain=True,
                                             flight_mode=FlightMode.FLY) == 12
    assert get_effective_movement_in_terrain(flyer, in_difficult_terrain=True,
                                             flight_mode=FlightMode.GROUND) == 2
    assert get_effective_movement_in_terrain(flyer, flight_mode=FlightMode.GROUND) == 4


def test_cannot_start_flying_inside_woodland():
    with pytest.raises(ValueError, match="woodland"):
        flight_movement(_flying(), FlightMode.FLY, currently_in_woodland=True)


@pytest.mark.parametrize("bad", [
    {"overlaps_model": True}, {"in_woodland": True},
    {"stable_surface": False}, {"enemy_reachable_surface": False},
    {"bridges_passage_underneath": True},
])
def test_flight_landing_prohibitions(bad):
    assert not validate_flight_landing(_landing(**bad))


def test_unknown_landing_evidence_fails_closed():
    with pytest.raises(ValueError, match="evidence"):
        validate_flight_landing(FlightLanding())


def test_control_zone_landing_requires_charge():
    landing = _landing(enemy_control_zone=True, charges_control_zone_owner=True)
    assert not validate_flight_landing(landing)
    assert validate_flight_landing(landing, charging=True)
    with pytest.raises(ValueError, match="charge evidence"):
        validate_flight_landing(_landing(enemy_control_zone=True), charging=True)


def test_engaged_target_cannot_land_in_other_control_zone():
    landing = _landing(target_already_engaged=True, other_enemy_control_zone=True)
    assert not validate_flight_landing(landing, charging=True)
    assert validate_flight_landing(_landing(target_already_engaged=True,
                                           other_enemy_control_zone=False), charging=True)


def test_production_war_bat_rule():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    bat = ConfiguredProfile(profiles["WAR_BAT"])
    assert has_fly(bat)
    assert flight_movement(bat, FlightMode.GROUND).distance_inches == 4
