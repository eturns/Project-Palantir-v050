"""DEV-077S-I2-H3-B: evidence-based objective reachability.

Calculates conditional travel ceilings, not paths, occupations or scores.
Movement comes from the verified terrain_movement engine or an explicitly
supplied evidence value. No legacy Mobility index is treated as inches.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from math import isfinite

class ReachabilityCheck(str, Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ObjectiveTravelEvidence:
    model_id: str
    objective_id: str
    distance_inches: Fraction
    turns_available: int
    movement_inches_per_turn: Fraction
    route_legal: ReachabilityCheck
    placement_legal: ReachabilityCheck
    terrain_route_verified: ReachabilityCheck
    movement_available: ReachabilityCheck = ReachabilityCheck.VERIFIED_TRUE

    def __post_init__(self):
        if not self.model_id or not self.objective_id:
            raise ValueError("model and objective IDs must be nonblank")
        for name in ("distance_inches", "movement_inches_per_turn"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, Fraction)) or value < 0:
                raise ValueError(f"{name} must be a nonnegative exact distance")
        if isinstance(self.turns_available, bool) or not isinstance(self.turns_available, int) or self.turns_available < 0:
            raise ValueError("turns_available must be nonnegative integer")
        for name in ("route_legal", "placement_legal", "terrain_route_verified", "movement_available"):
            if not isinstance(getattr(self, name), ReachabilityCheck):
                raise TypeError(f"{name} must be ReachabilityCheck")


@dataclass(frozen=True)
class ObjectiveReachability:
    model_id: str
    objective_id: str
    minimum_turns_at_declared_speed: int | None
    maximum_travel_inches: Fraction
    status: str
    evidence_status: str = "conditional_geometry_only"
    occupation_verified: None = None
    control_verified: None = None
    victory_points: None = None
    dashboard_score: None = None
    scenario_score: None = None


def assess_objective_reachability(evidence: ObjectiveTravelEvidence) -> ObjectiveReachability:
    if not isinstance(evidence, ObjectiveTravelEvidence):
        raise TypeError("evidence must be ObjectiveTravelEvidence")
    ceiling = evidence.movement_inches_per_turn * evidence.turns_available
    needed = (0 if evidence.distance_inches == 0 else
              None if evidence.movement_inches_per_turn == 0 else
              -(-evidence.distance_inches // evidence.movement_inches_per_turn))
    checks = (evidence.route_legal, evidence.placement_legal,
              evidence.terrain_route_verified, evidence.movement_available)
    if ReachabilityCheck.VERIFIED_FALSE in checks:
        status = "blocked"
    elif ReachabilityCheck.UNKNOWN in checks:
        status = "unresolved"
    elif evidence.distance_inches > ceiling:
        status = "beyond_declared_turn_ceiling"
    else:
        status = "conditionally_reachable"
    return ObjectiveReachability(
        model_id=evidence.model_id, objective_id=evidence.objective_id,
        minimum_turns_at_declared_speed=needed,
        maximum_travel_inches=ceiling, status=status,
    )


def movement_for_declared_terrain(
    combatant, *, in_difficult_terrain: bool = False,
    is_water_feature: bool = False,
) -> Fraction:
    """Use actual configured movement, not an army's accessibility index.

    This does not prove a path traverses only the selected terrain category.
    """
    from terrain_movement import get_effective_movement_in_terrain
    value = get_effective_movement_in_terrain(
        combatant, in_difficult_terrain=in_difficult_terrain,
        is_water_feature=is_water_feature,
    )
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) or value < 0:
        raise ValueError("terrain movement must be a finite nonnegative distance")
    return Fraction(str(value))
