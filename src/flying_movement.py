"""2024 Fly: reusable voluntary flying/ground movement and landing validation.

This module does not infer geometry, control zones, activation permission or
terrain features. Callers supply observed battlefield facts.
"""
from dataclasses import dataclass
from enum import Enum

FLY_RULE_ID = "FLY"


class FlightMode(Enum):
    FLY = "fly"
    GROUND = "ground"


@dataclass(frozen=True)
class FlightLanding:
    """Observed endpoint/landing facts; None denotes unknown, not legal."""
    overlaps_model: bool | None = None
    in_woodland: bool | None = None
    stable_surface: bool | None = None
    enemy_reachable_surface: bool | None = None
    bridges_passage_underneath: bool | None = None
    enemy_control_zone: bool | None = None
    charges_control_zone_owner: bool | None = None
    other_enemy_control_zone: bool | None = None
    target_already_engaged: bool | None = None


@dataclass(frozen=True)
class FlightMovement:
    distance_inches: float
    ignores_intervening_models_and_terrain: bool
    ignores_vertical_distance: bool
    ignores_enemy_control_zones_en_route: bool
    may_enter_woodland: bool


def _configured(model):
    return getattr(model, "active_configured_profile", model)


def has_fly(model) -> bool:
    cfg = _configured(model)
    return any(
        getattr(getattr(assignment, "rule", None), "id", None) == FLY_RULE_ID
        for assignment in getattr(cfg, "effective_special_rules", ())
    )


def flight_movement(model, mode: FlightMode, *,
                    currently_in_woodland: bool = False) -> FlightMovement:
    if not isinstance(mode, FlightMode):
        raise TypeError("mode must be FlightMode")
    if type(currently_in_woodland) is not bool:
        raise TypeError("currently_in_woodland must be bool")
    if not has_fly(model):
        raise ValueError("Model does not possess Fly")
    if mode is FlightMode.FLY:
        if currently_in_woodland:
            raise ValueError("Cannot begin flying until completely outside woodland")
        distance = _configured(model).effective_movement
        return FlightMovement(float(distance), True, True, True, False)
    return FlightMovement(4.0, False, False, False, True)


def validate_flight_landing(facts: FlightLanding, *,
                            charging: bool = False,
                            intermediate_landing: bool = False) -> bool:
    """True only if every relevant condition is explicitly verified.

    Return False for known prohibitions. Raise ValueError on missing information
    rather than silently crediting an unverified legal landing.
    """
    if not isinstance(facts, FlightLanding):
        raise TypeError("facts must be FlightLanding")
    if type(charging) is not bool or type(intermediate_landing) is not bool:
        raise TypeError("landing flags must be bool")
    required = (
        "overlaps_model", "in_woodland", "stable_surface",
        "enemy_reachable_surface", "bridges_passage_underneath",
        "enemy_control_zone",
    )
    for name in required:
        value = getattr(facts, name)
        if type(value) is not bool:
            raise ValueError(f"Landing evidence missing for {name}")
    if (facts.overlaps_model or facts.in_woodland or not facts.stable_surface
            or not facts.enemy_reachable_surface or facts.bridges_passage_underneath):
        return False
    if facts.enemy_control_zone:
        if type(facts.charges_control_zone_owner) is not bool:
            raise ValueError("Landing in control zone requires explicit charge evidence")
        if not charging or not facts.charges_control_zone_owner:
            return False
    if charging and facts.target_already_engaged is True:
        if type(facts.other_enemy_control_zone) is not bool:
            raise ValueError("Engaged target requires other control-zone evidence")
        if facts.other_enemy_control_zone:
            return False
    return True
