"""DEV-077S-I2-D-C2: non-scoring army mobility aggregation.

Mechanical measurements are kept in their original units; no terrain mixture,
reposition bonus or 0-1 calibration is assumed here. Production scoring unchanged.
"""
from dataclasses import dataclass
from math import isfinite

from army import Army
from mobility_mechanical_comparison import compare_army_mobility


@dataclass(frozen=True)
class ArmyMobilityAggregation:
    model_count: int
    army_points: int
    average_open_ground: float
    average_difficult_terrain: float
    total_open_ground: float
    total_difficult_terrain: float
    open_ground_per_100_points: float
    difficult_terrain_per_100_points: float
    terrain_retention: float
    legacy_average: float
    self_reposition_models: int
    anchor_reposition_models: int
    eligible_anchor_pairs: int

    @property
    def reposition_requires_context(self) -> bool:
        return self.self_reposition_models > 0 or self.eligible_anchor_pairs > 0


def aggregate_army_mobility(army: Army, *, form_states=None) -> ArmyMobilityAggregation:
    """Aggregate movement accessibility for actual fielded model quantities.

    Per-model movement is adjusted for base size by the existing engine.
    Totals represent sums of model-level movement-accessibility scores, not
    attainable objective coverage or literal summed inches of army movement.
    Reposition abilities remain conditional diagnostics, never free distance.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    result = compare_army_mobility(army, form_states=form_states)
    points = army.total_points()
    if points < 0:
        raise ValueError("army points cannot be negative")
    count = result.model_count
    open_total = result.open_ground_manoeuvrability * count
    difficult_total = result.difficult_terrain_manoeuvrability * count
    if not all(isfinite(v) for v in (open_total, difficult_total, points)):
        raise ValueError("mobility measurements must be finite")
    return ArmyMobilityAggregation(
        model_count=count,
        army_points=points,
        average_open_ground=result.open_ground_manoeuvrability,
        average_difficult_terrain=result.difficult_terrain_manoeuvrability,
        total_open_ground=open_total,
        total_difficult_terrain=difficult_total,
        open_ground_per_100_points=(open_total * 100 / points if points else 0.0),
        difficult_terrain_per_100_points=(difficult_total * 100 / points if points else 0.0),
        terrain_retention=result.terrain_retention,
        legacy_average=result.legacy_manoeuvrability,
        self_reposition_models=result.self_reposition_models,
        anchor_reposition_models=result.anchor_reposition_models,
        eligible_anchor_pairs=result.eligible_anchor_pairs,
    )
