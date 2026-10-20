"""Terrain movement: existing mechanics plus scoped Woodland Creature.

Woodland Creature exemption applies only when terrain is explicitly woodland.
Spatial clearance/base-size logic remains outside this distance resolver.
"""
from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from profile_classification import ModelType

HUNT_MASTER_RULE_ID = "HUNT_MASTER"
SPECTRAL_WALK_RULE_ID = "SPECTRAL_WALK"
SWIFT_MOVEMENT_RULE_ID = "SWIFT_MOVEMENT"
WOODLAND_CREATURE_RULE_ID = "WOODLAND_CREATURE"


def _configured_profile_from_combatant(combatant: ConfiguredProfile | FieldedModelFormState) -> ConfiguredProfile:
    if isinstance(combatant, FieldedModelFormState):
        return combatant.active_configured_profile
    return combatant


def _has_rule(combatant: ConfiguredProfile | FieldedModelFormState, rule_id: str) -> bool:
    profile = _configured_profile_from_combatant(combatant)
    return any(a.rule.id == rule_id for a in profile.effective_special_rules)


@dataclass(frozen=True)
class TerrainTraversalCapabilities:
    """Existing broad movement exemptions; woodland is separately contextual."""
    ignore_non_water_difficult_terrain: bool
    ignore_water_difficult_terrain: bool
    automatic_climb_jump_leap_swim_six: bool
    ignore_obstacles_without_climb_or_jump_test: bool
    vertical_distance_counts_toward_move: bool


def terrain_traversal_capabilities(combatant: ConfiguredProfile | FieldedModelFormState) -> TerrainTraversalCapabilities:
    spectral = _has_rule(combatant, SPECTRAL_WALK_RULE_ID)
    swift = _has_rule(combatant, SWIFT_MOVEMENT_RULE_ID)
    hunt_master_cavalry = (
        _has_rule(combatant, HUNT_MASTER_RULE_ID)
        and ModelType.CAVALRY in combatant.effective_model_types
    )
    return TerrainTraversalCapabilities(
        ignore_non_water_difficult_terrain=(spectral or swift or hunt_master_cavalry),
        ignore_water_difficult_terrain=spectral or hunt_master_cavalry,
        automatic_climb_jump_leap_swim_six=spectral,
        ignore_obstacles_without_climb_or_jump_test=swift,
        vertical_distance_counts_toward_move=swift,
    )


def ignores_difficult_terrain_movement_penalty(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    is_water_feature: bool = False,
    is_woodland: bool = False,
) -> bool:
    """Woodland Creature exempts woodland only, not unrelated rough terrain.

    Preserve historical exceptions for Spectral Walk, Swift Movement and
    Hunt Master. Contradictory water+woodland tagging is rejected.
    """
    if is_water_feature and is_woodland:
        raise ValueError("Terrain cannot be both a water feature and woodland.")
    caps = terrain_traversal_capabilities(combatant)
    if is_woodland and _has_rule(combatant, WOODLAND_CREATURE_RULE_ID):
        return True
    return (
        caps.ignore_water_difficult_terrain
        if is_water_feature else caps.ignore_non_water_difficult_terrain
    )


def get_effective_movement_in_terrain(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    in_difficult_terrain: bool = False,
    is_water_feature: bool = False,
    is_woodland: bool = False,
    flight_mode=None,
    currently_in_woodland: bool = False,
) -> float:
    """Movement inches for terrain, optionally with an explicit Fly mode."""
    if is_water_feature and is_woodland:
        raise ValueError("Terrain cannot be both a water feature and woodland.")
    # Fly is an elected mode, not a permanent terrain exemption.
    # The optional keyword preserves all existing call sites.
    if flight_mode is not None:
        from flying_movement import FlightMode, flight_movement
        result = flight_movement(
            combatant, flight_mode,
            currently_in_woodland=currently_in_woodland,
        )
        if flight_mode is FlightMode.FLY:
            return result.distance_inches
        # Grounded Flyers have 4-inch movement and ordinary terrain rules.
        movement = result.distance_inches
    else:
        movement = combatant.effective_movement
    if not in_difficult_terrain:
        return float(movement)
    if ignores_difficult_terrain_movement_penalty(
        combatant, is_water_feature=is_water_feature, is_woodland=is_woodland
    ):
        return float(movement)
    return movement / 2
