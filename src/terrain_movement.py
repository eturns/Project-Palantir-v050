"""Movement through terrain, using configured and runtime form-state mechanics.

DEV-077S-I2-D-B4a. This is a complete replacement for src/terrain_movement.py.
It preserves the old public API and the Hunt Master cavalry condition.
It does not change manoeuvrability scoring or the base-size accessibility proxy.
"""
from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from profile_classification import ModelType

HUNT_MASTER_RULE_ID = "HUNT_MASTER"
SPECTRAL_WALK_RULE_ID = "SPECTRAL_WALK"
SWIFT_MOVEMENT_RULE_ID = "SWIFT_MOVEMENT"


def _configured_profile_from_combatant(
    combatant: ConfiguredProfile | FieldedModelFormState,
) -> ConfiguredProfile:
    if isinstance(combatant, FieldedModelFormState):
        return combatant.active_configured_profile
    return combatant


def _has_rule(combatant: ConfiguredProfile | FieldedModelFormState, rule_id: str) -> bool:
    profile = _configured_profile_from_combatant(combatant)
    return any(a.rule.id == rule_id for a in profile.effective_special_rules)


@dataclass(frozen=True)
class TerrainTraversalCapabilities:
    """Declarative travel properties; these do not assert a successful move.

    Base size and available placement geometry must still be checked by future
    spatial/pathfinding consumers, even when an obstacle test is bypassed.
    """
    ignore_non_water_difficult_terrain: bool
    ignore_water_difficult_terrain: bool
    automatic_climb_jump_leap_swim_six: bool
    ignore_obstacles_without_climb_or_jump_test: bool
    vertical_distance_counts_toward_move: bool


def terrain_traversal_capabilities(
    combatant: ConfiguredProfile | FieldedModelFormState,
) -> TerrainTraversalCapabilities:
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
) -> bool:
    """Return whether the supplied terrain category is exempt from slowdown.

    Hunt Master's pre-existing terrain exemption is retained as originally
    modelled; no new water exception is inferred for that special rule.
    """
    caps = terrain_traversal_capabilities(combatant)
    return (
        caps.ignore_water_difficult_terrain
        if is_water_feature else caps.ignore_non_water_difficult_terrain
    )


def get_effective_movement_in_terrain(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    in_difficult_terrain: bool = False,
    is_water_feature: bool = False,
) -> float:
    """Return movement distance; vertical geometry remains a separate concern."""
    movement = combatant.effective_movement
    if not in_difficult_terrain:
        return float(movement)
    if ignores_difficult_terrain_movement_penalty(
        combatant, is_water_feature=is_water_feature
    ):
        return float(movement)
    return movement / 2
