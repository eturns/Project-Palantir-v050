"""DEV-077S-I2-H3-C: Dominant-aware objective contribution and endurance.

Produces an explicit, conditional snapshot using the existing 2024 presence
resolver. Does not infer Courage tests, survival, Control, paths or victory
points. A verified position is not proof of future scoring endurance.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

from configured_profile import ConfiguredProfile
from profiles import Profile
from scenario_presence import calculate_profile_scenario_presence
from objective_position_evidence import (
    ObjectiveLocation, ObjectiveModelPosition, ObjectivePositionReport,
    ObjectiveVerification, assess_objective_positions,
)


class EnduranceCheck(str, Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ObjectiveEnduranceModel:
    model_id: str
    army_id: str
    profile: Profile | ConfiguredProfile
    x_inches: Fraction | None
    y_inches: Fraction | None
    scenario_eligible: ObjectiveVerification
    alive_at_scoring: EnduranceCheck = EnduranceCheck.UNKNOWN
    courage_requirement_satisfied: EnduranceCheck = EnduranceCheck.UNKNOWN
    control_allows_contribution: EnduranceCheck = EnduranceCheck.UNKNOWN

    def __post_init__(self):
        if not isinstance(self.profile, (Profile, ConfiguredProfile)):
            raise TypeError("profile must be a Profile or ConfiguredProfile")
        for field in ("alive_at_scoring", "courage_requirement_satisfied", "control_allows_contribution"):
            if not isinstance(getattr(self, field), EnduranceCheck):
                raise TypeError(f"{field} must be EnduranceCheck")


@dataclass(frozen=True)
class ObjectiveEnduranceReport:
    current_snapshot: ObjectivePositionReport
    scoring_snapshot: ObjectivePositionReport
    presence_by_model: tuple[tuple[str, int], ...]
    unresolved_endurance_models: tuple[str, ...]
    evidence_status: str = "conditional_endurance_not_future_outcome"
    dashboard_score: None = None
    scenario_score: None = None
    victory_points: None = None


def _scoring_eligibility(model: ObjectiveEnduranceModel) -> ObjectiveVerification:
    checks = (model.alive_at_scoring, model.courage_requirement_satisfied,
              model.control_allows_contribution)
    if model.scenario_eligible is ObjectiveVerification.FALSE or EnduranceCheck.VERIFIED_FALSE in checks:
        return ObjectiveVerification.FALSE
    if model.scenario_eligible is ObjectiveVerification.UNKNOWN or EnduranceCheck.UNKNOWN in checks:
        return ObjectiveVerification.UNKNOWN
    return ObjectiveVerification.TRUE


def assess_objective_endurance(
    objective: ObjectiveLocation,
    models: tuple[ObjectiveEnduranceModel, ...],
) -> ObjectiveEnduranceReport:
    """Only verified scoring-time conditions may establish scoring presence.

    Unknown conditions remain unknown even when present-board coordinates are
    known. Dominant (X) affects effective presence, not wound endurance.
    """
    if not isinstance(models, tuple) or any(not isinstance(m, ObjectiveEnduranceModel) for m in models):
        raise TypeError("models must be ObjectiveEnduranceModel tuple")
    current = []
    future = []
    weights = []
    unknown = []
    for m in models:
        weight = calculate_profile_scenario_presence(m.profile)
        weights.append((m.model_id, weight))
        common = dict(model_id=m.model_id, army_id=m.army_id,
                      x_inches=m.x_inches, y_inches=m.y_inches,
                      effective_presence=weight)
        current.append(ObjectiveModelPosition(
            scenario_eligible=m.scenario_eligible, **common))
        score_eligible = _scoring_eligibility(m)
        future.append(ObjectiveModelPosition(
            scenario_eligible=score_eligible, **common))
        if score_eligible is ObjectiveVerification.UNKNOWN:
            unknown.append(m.model_id)
    return ObjectiveEnduranceReport(
        current_snapshot=assess_objective_positions(objective, tuple(current)),
        scoring_snapshot=assess_objective_positions(objective, tuple(future)),
        presence_by_model=tuple(weights),
        unresolved_endurance_models=tuple(unknown),
    )
