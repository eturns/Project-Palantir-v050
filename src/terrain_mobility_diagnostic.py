"""DEV-077S-I2-D-B1: mechanical terrain mobility diagnostic.

This module deliberately does not change legacy manoeuvrability or scenario scoring.
It reports movement/base-accessibility under two terrain conditions; ability-tag
bonuses and scenario projection belong to separate calculations.
"""
from dataclasses import dataclass

from army import Army
from fielded_model_form_state import FieldedModelFormState
from manoeuvrability_inputs import ManoeuvrabilityInputs
from manoeuvrability_score import calculate_manoeuvrability
from terrain_movement import get_effective_movement_in_terrain


@dataclass(frozen=True)
class TerrainMobilityDiagnostic:
    open_ground: float
    difficult_terrain: float
    terrain_retention: float
    model_count: int


def calculate_terrain_mobility_diagnostic(
    army: Army,
    *,
    form_states: tuple[FieldedModelFormState, ...] | None = None,
) -> TerrainMobilityDiagnostic:
    """Return model-weighted, base-adjusted movement under two terrain states.

    terrain_retention is difficult_terrain/open_ground (0 when open_ground=0).
    No special-rule tag scores are added: terrain effects come from the existing
    movement engine, not arbitrary valuation weights.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army.")

    model_count = army.model_count()
    if form_states is None:
        combatants = tuple(
            (entry.configured_profile, entry.quantity)
            for entry in army.entries
            if entry.counts_as_model
        )
    else:
        expected_ids = {
            model.id for model in army.fielded_models()
            if model.counts_as_model
        }
        supplied_ids = [state.fielded_model_id for state in form_states]
        if (len(supplied_ids) != len(expected_ids)
                or set(supplied_ids) != expected_ids):
            raise ValueError(
                "Form states must contain exactly one state for every fielded model."
            )
        combatants = tuple((state, 1) for state in form_states)

    if model_count == 0:
        return TerrainMobilityDiagnostic(0.0, 0.0, 0.0, 0)

    open_total = 0.0
    difficult_total = 0.0
    for combatant, quantity in combatants:
        base = combatant.effective_base_size_mm
        open_movement = get_effective_movement_in_terrain(
            combatant, in_difficult_terrain=False
        )
        difficult_movement = get_effective_movement_in_terrain(
            combatant, in_difficult_terrain=True
        )
        open_total += quantity * calculate_manoeuvrability(
            ManoeuvrabilityInputs(movement=open_movement, base_size_mm=base)
        )
        difficult_total += quantity * calculate_manoeuvrability(
            ManoeuvrabilityInputs(movement=difficult_movement, base_size_mm=base)
        )

    open_ground = open_total / model_count
    difficult_terrain = difficult_total / model_count
    return TerrainMobilityDiagnostic(
        open_ground=open_ground,
        difficult_terrain=difficult_terrain,
        terrain_retention=(difficult_terrain / open_ground if open_ground else 0.0),
        model_count=model_count,
    )
