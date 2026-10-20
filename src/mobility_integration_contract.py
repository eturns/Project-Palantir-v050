"""DEV-077S-I2-D-D4 — read-only mechanical Mobility integration contract.

This is a typed boundary for future consumers, not a scoring adapter.
No provisional terrain blend, reposition distance, or dashboard score is created.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Literal

from army import Army
from army_mobility_aggregation import aggregate_army_mobility

EVIDENCE_STATUS = "diagnostic_validated_not_calibrated"
METRIC_VERSION = "I2-D-D4.1"


@dataclass(frozen=True)
class MobilityMeasure:
    metric_id: str
    metric_version: str
    value: float
    unit: str
    aggregation: str
    assumptions: tuple[str, ...]
    evidence_status: str
    dependencies: tuple[str, ...]


@dataclass(frozen=True)
class MobilityIntegrationContract:
    open_ground: MobilityMeasure
    difficult_terrain: MobilityMeasure
    terrain_retention: MobilityMeasure
    legacy_comparator: MobilityMeasure
    model_count: int
    army_points: int
    self_reposition_models: int
    anchor_reposition_models: int
    potential_anchor_pairs: int
    dashboard_score: None = None
    scenario_score: None = None
    calibration_status: Literal["pending"] = "pending"


def _measure(key, value, unit, aggregation, assumptions, dependencies):
    if not isfinite(value):
        raise ValueError("Mobility measure must be finite")
    return MobilityMeasure(
        metric_id=key,
        metric_version=METRIC_VERSION,
        value=value,
        unit=unit,
        aggregation=aggregation,
        assumptions=tuple(assumptions),
        evidence_status=EVIDENCE_STATUS,
        dependencies=tuple(dependencies),
    )


def build_mobility_integration_contract(
    army: Army, *, form_states=None
) -> MobilityIntegrationContract:
    """Preserve raw movement, provenance and legacy comparison separately.

    The movement index is movement adjusted for model base-size accessibility.
    It is NOT literal inches travelled, board coverage, or an objective score.
    """
    a = aggregate_army_mobility(army, form_states=form_states)
    common = ("configured model movement", "base-size accessibility penalty",
              "fielded model quantity weighted")
    mechanics = ("army_mobility_aggregation", "terrain_movement", "manoeuvrability_score")
    return MobilityIntegrationContract(
        open_ground=_measure(
            "mobility.open_ground.mean", a.average_open_ground,
            "movement_accessibility_index", "mean_per_fielded_model",
            common + ("open ground",), mechanics,
        ),
        difficult_terrain=_measure(
            "mobility.difficult_terrain.mean", a.average_difficult_terrain,
            "movement_accessibility_index", "mean_per_fielded_model",
            common + ("generic difficult terrain; terrain-specific exceptions apply",),
            mechanics,
        ),
        terrain_retention=_measure(
            "mobility.terrain_retention", a.terrain_retention,
            "dimensionless_ratio", "difficult_divided_by_open",
            ("zero-model armies return zero",), mechanics,
        ),
        legacy_comparator=_measure(
            "mobility.legacy.average", a.legacy_average,
            "legacy_manoeuvrability_index", "legacy_mean_per_fielded_model",
            ("comparison only; must not feed mechanical scoring",),
            ("army_manoeuvrability",),
        ),
        model_count=a.model_count,
        army_points=a.army_points,
        self_reposition_models=a.self_reposition_models,
        anchor_reposition_models=a.anchor_reposition_models,
        potential_anchor_pairs=a.eligible_anchor_pairs,
    )

# DEV-077-GUN-C6-C4: optional War Beast Trample contact evidence
from gundabad_trample_movement_evidence import build_trample_movement_evidence


def build_troll_brute_trample_movement_evidence(
    combatant, *, is_trampling: bool, contacts: tuple
):
    """Diagnostic-only bridge; never changes calibrated mobility measures."""
    return build_trample_movement_evidence(
        combatant, is_trampling=is_trampling, contacts=contacts,
    )
