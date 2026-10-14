"""DEV-077S-I2-H3-A: conditional positions, objective access and contest evidence.

Evidence-only model. Does not infer scenario scoring, objective-specific
eligibility, movement path, enemy reactions or dashboard capability ratings.
Distances and coverage radii are supplied by a caller with battlefield evidence.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction


class ObjectiveVerification(str, Enum):
    TRUE = "verified_true"
    FALSE = "verified_false"
    UNKNOWN = "unresolved"


class ObjectivePresenceStatus(str, Enum):
    WITHIN_RANGE = "within_range"
    OUTSIDE_RANGE = "outside_range"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ObjectiveLocation:
    objective_id: str
    x_inches: Fraction
    y_inches: Fraction
    capture_radius_inches: Fraction

    def __post_init__(self):
        _identifier(self.objective_id, "objective_id")
        for field in ("x_inches", "y_inches", "capture_radius_inches"):
            _fraction(getattr(self, field), field)
        if self.capture_radius_inches < 0:
            raise ValueError("capture radius cannot be negative")


@dataclass(frozen=True)
class ObjectiveModelPosition:
    model_id: str
    army_id: str
    x_inches: Fraction | None
    y_inches: Fraction | None
    scenario_eligible: ObjectiveVerification
    effective_presence: int = 1

    def __post_init__(self):
        _identifier(self.model_id, "model_id")
        _identifier(self.army_id, "army_id")
        if (self.x_inches is None) != (self.y_inches is None):
            raise ValueError("position coordinates must both be supplied or unknown")
        if self.x_inches is not None:
            _fraction(self.x_inches, "x_inches")
            _fraction(self.y_inches, "y_inches")
        _verification(self.scenario_eligible)
        if (isinstance(self.effective_presence, bool)
                or not isinstance(self.effective_presence, int)
                or self.effective_presence < 1):
            raise ValueError("effective_presence must be a positive integer")


@dataclass(frozen=True)
class ModelObjectiveEvidence:
    objective_id: str
    model_id: str
    army_id: str
    position_status: ObjectivePresenceStatus
    eligibility: ObjectiveVerification
    verified_presence: int
    potentially_eligible: bool


@dataclass(frozen=True)
class ObjectivePositionReport:
    objective_id: str
    model_evidence: tuple[ModelObjectiveEvidence, ...]
    verified_presence_by_army: tuple[tuple[str, int], ...]
    unresolved_model_count: int
    controlling_army_id: str | None
    status: str
    evidence_status: str = "conditional_position_snapshot_only"
    dashboard_score: None = None
    scenario_score: None = None


def _identifier(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string")


def _fraction(value, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Fraction):
        raise TypeError(f"{field} must be Fraction")


def _verification(value) -> None:
    if not isinstance(value, ObjectiveVerification):
        raise TypeError("scenario_eligible must be ObjectiveVerification")


def assess_objective_positions(
    objective: ObjectiveLocation,
    models: tuple[ObjectiveModelPosition, ...],
) -> ObjectivePositionReport:
    """Resolve a position snapshot when all competing evidence is complete.

    No winning side is assigned if any unresolved model might contest.
    Equal verified presence is contested; no scoring points are inferred.
    """
    if not isinstance(objective, ObjectiveLocation):
        raise TypeError("objective must be ObjectiveLocation")
    if not isinstance(models, tuple) or any(
        not isinstance(m, ObjectiveModelPosition) for m in models
    ):
        raise TypeError("models must be a tuple of ObjectiveModelPosition")
    ids = [m.model_id for m in models]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate model_id in objective snapshot")
    observations = []
    totals: dict[str, int] = {}
    unknown = 0
    for model in models:
        if model.x_inches is None:
            position = ObjectivePresenceStatus.UNRESOLVED
        else:
            dx = model.x_inches - objective.x_inches
            dy = model.y_inches - objective.y_inches
            radius = objective.capture_radius_inches
            position = (ObjectivePresenceStatus.WITHIN_RANGE
                        if dx * dx + dy * dy <= radius * radius
                        else ObjectivePresenceStatus.OUTSIDE_RANGE)
        verified = (position is ObjectivePresenceStatus.WITHIN_RANGE
                    and model.scenario_eligible is ObjectiveVerification.TRUE)
        possible = (position is not ObjectivePresenceStatus.OUTSIDE_RANGE
                    and model.scenario_eligible is not ObjectiveVerification.FALSE)
        if possible and not verified:
            unknown += 1
        contribution = model.effective_presence if verified else 0
        totals[model.army_id] = totals.get(model.army_id, 0) + contribution
        observations.append(ModelObjectiveEvidence(
            objective.objective_id, model.model_id, model.army_id,
            position, model.scenario_eligible, contribution, possible,
        ))
    nonzero = sorted(((army, value) for army, value in totals.items() if value),
                     key=lambda pair: (-pair[1], pair[0]))
    if unknown:
        winner, status = None, "unresolved_competing_evidence"
    elif not nonzero:
        winner, status = None, "unoccupied"
    elif len(nonzero) > 1 and nonzero[0][1] == nonzero[1][1]:
        winner, status = None, "contested_equal_presence"
    else:
        winner, status = nonzero[0][0], "verified_presence_leader"
    return ObjectivePositionReport(
        objective_id=objective.objective_id,
        model_evidence=tuple(observations),
        verified_presence_by_army=tuple(sorted(totals.items())),
        unresolved_model_count=unknown,
        controlling_army_id=winner,
        status=status,
    )
