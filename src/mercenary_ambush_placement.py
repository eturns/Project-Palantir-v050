"""DEV-077-GUN-C5-B2: spatial-evidence contract for Mercenary Ambush.

The caller, not this resolver, assesses real tabletop geometry and agrees
eligible terrain with the opponent. An unknown survey never authorises an
arbitrary reinforcement fallback. No models are created or moved here.
"""
from dataclasses import dataclass
from enum import Enum


class PlacementMethod(Enum):
    TERRAIN = "terrain"
    REINFORCEMENTS = "reinforcements"


class PlacementEvidence(Enum):
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AmbushTerrainCandidate:
    """Evidence for placing *every* member of one warband at a terrain piece.

    terrain_agreed: opponent and controlling player agreed it is eligible.
    whole_warband_fits: every model can be fully inside or in base contact.
    outside_enemy_control_zones: no member ends in an enemy Control Zone.
    Evidence may be UNKNOWN where positions have not been checked.
    """

    terrain_id: str
    terrain_agreed: PlacementEvidence
    whole_warband_fits: PlacementEvidence
    outside_enemy_control_zones: PlacementEvidence

    def __post_init__(self) -> None:
        if not isinstance(self.terrain_id, str) or not self.terrain_id.strip():
            raise ValueError("A terrain identifier is required.")
        for field_name in (
            "terrain_agreed", "whole_warband_fits", "outside_enemy_control_zones"
        ):
            if not isinstance(getattr(self, field_name), PlacementEvidence):
                raise TypeError(f"{field_name} must be PlacementEvidence.")

    @property
    def is_legal(self) -> bool:
        return all(
            getattr(self, name) is PlacementEvidence.CONFIRMED
            for name in (
                "terrain_agreed", "whole_warband_fits", "outside_enemy_control_zones"
            )
        )

    @property
    def is_definitively_impossible(self) -> bool:
        return any(
            getattr(self, name) is PlacementEvidence.REJECTED
            for name in (
                "terrain_agreed", "whole_warband_fits", "outside_enemy_control_zones"
            )
        )


@dataclass(frozen=True)
class AmbushPlacementPlan:
    warband_id: str
    method: PlacementMethod
    terrain_id: str | None = None


def plan_mercenary_ambush_placement(
    *,
    warband_id: str,
    warband_model_count: int,
    candidates: tuple[AmbushTerrainCandidate, ...],
    survey_complete: bool,
    selected_terrain_id: str | None = None,
) -> AmbushPlacementPlan:
    """Return a permitted *method*, not an actual placement or movement.

    Only a complete survey proving no legal terrain candidate can permit
    the table-edge Reinforcements fallback. Unknown geometry fails closed.
    The controlling player must explicitly select between legal candidates.
    """
    if not isinstance(warband_id, str) or not warband_id.strip():
        raise ValueError("Warband ID is required.")
    if type(warband_model_count) is not int or warband_model_count < 1:
        raise ValueError("Warband model count must be a positive integer.")
    if type(survey_complete) is not bool:
        raise TypeError("survey_complete must be bool.")
    if not isinstance(candidates, tuple) or any(
        not isinstance(candidate, AmbushTerrainCandidate) for candidate in candidates
    ):
        raise TypeError("Candidates must be a tuple of AmbushTerrainCandidate.")
    terrain_ids = [candidate.terrain_id for candidate in candidates]
    if len(terrain_ids) != len(set(terrain_ids)):
        raise ValueError("Terrain identifiers must be unique.")
    if selected_terrain_id is not None and selected_terrain_id not in terrain_ids:
        raise ValueError("Selected terrain was not surveyed.")

    legal = [candidate for candidate in candidates if candidate.is_legal]
    if selected_terrain_id is not None:
        if not any(candidate.terrain_id == selected_terrain_id for candidate in legal):
            raise ValueError("Selected terrain has no verified legal placement.")
        return AmbushPlacementPlan(warband_id, PlacementMethod.TERRAIN, selected_terrain_id)
    if legal:
        if len(legal) > 1:
            raise ValueError("Multiple legal terrain pieces: choose one explicitly.")
        return AmbushPlacementPlan(warband_id, PlacementMethod.TERRAIN, legal[0].terrain_id)

    if not survey_complete:
        raise ValueError("Cannot select Reinforcements before a complete terrain survey.")
    if any(not candidate.is_definitively_impossible for candidate in candidates):
        raise ValueError("Unknown terrain evidence cannot justify Reinforcements.")
    return AmbushPlacementPlan(warband_id, PlacementMethod.REINFORCEMENTS)
