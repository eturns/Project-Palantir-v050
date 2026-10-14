"""DEV-077S-I2-H3-D: scenario-aware Objective evidence, not legacy scores.

The catalogue provides scenario family, demands and termination, but does not
encode capture radii, VP schedules, or all special scoring exceptions. Those
must be supplied as verified rules before any VP can be calculated.
"""
from dataclasses import dataclass
from enum import Enum

from scenario_catalogue import OFFICIAL_SCENARIOS
from scenario_definition import ScenarioPool
from objective_position_evidence import ObjectiveLocation
from objective_endurance import ObjectiveEnduranceModel, ObjectiveEnduranceReport, assess_objective_endurance


class PresencePolicy(str, Enum):
    DOMINANT_ALLOWED = "dominant_allowed"
    ONE_PER_MODEL = "one_per_model"
    UNVERIFIED = "unverified"


class ScenarioObjectiveStatus(str, Enum):
    CATALOGUE_NOT_HOLD_OBJECTIVE = "catalogue_not_hold_objective"
    NEEDS_SCENARIO_RULES = "needs_scenario_rules"
    EVIDENCE_READY = "evidence_ready"


@dataclass(frozen=True)
class VerifiedScenarioObjectiveRules:
    """Caller attests these values from the applicable scenario rules.

    No default radius/presence convention/VP schedule is assumed.
    """
    capture_radius_inches: object
    presence_policy: PresencePolicy
    scoring_at_observed_turn: bool

    def __post_init__(self):
        from fractions import Fraction
        if (not isinstance(self.capture_radius_inches, Fraction)
                or self.capture_radius_inches < 0):
            raise ValueError("capture radius must be a nonnegative Fraction")
        if not isinstance(self.presence_policy, PresencePolicy):
            raise TypeError("presence_policy must be PresencePolicy")
        if not isinstance(self.scoring_at_observed_turn, bool):
            raise TypeError("scoring_at_observed_turn must be bool")


@dataclass(frozen=True)
class ScenarioObjectiveEvidence:
    scenario_id: str
    scenario_pool: ScenarioPool
    status: ScenarioObjectiveStatus
    endurance: ObjectiveEnduranceReport | None
    presence_policy: PresencePolicy
    controlling_army_at_scoring: str | None
    victory_points: None = None
    dashboard_score: None = None
    scenario_score: None = None
    evidence_status: str = "catalogue_plus_explicit_scenario_rules"


def build_scenario_objective_evidence(
    scenario_id: str,
    objective: ObjectiveLocation | None,
    models: tuple[ObjectiveEnduranceModel, ...],
    *, rules: VerifiedScenarioObjectiveRules | None = None,
) -> ScenarioObjectiveEvidence:
    """Apply H3-A/C evidence only under explicit scenario-rule provenance.

    Unknown scoring eligibility, placement, and control remain unresolved.
    This never derives official VP totals or future battle outcomes.
    """
    catalog = {s.id: s for s in OFFICIAL_SCENARIOS}
    if scenario_id not in catalog:
        raise ValueError("scenario_id is not in official catalogue")
    scenario = catalog[scenario_id]
    if not isinstance(models, tuple) or any(not isinstance(m, ObjectiveEnduranceModel) for m in models):
        raise TypeError("models must be ObjectiveEnduranceModel tuple")
    if rules is not None and not isinstance(rules, VerifiedScenarioObjectiveRules):
        raise TypeError("rules must be VerifiedScenarioObjectiveRules or None")
    if scenario.pool is not ScenarioPool.HOLD_OBJECTIVE:
        return ScenarioObjectiveEvidence(scenario_id, scenario.pool,
            ScenarioObjectiveStatus.CATALOGUE_NOT_HOLD_OBJECTIVE, None,
            PresencePolicy.UNVERIFIED, None)
    if rules is None or objective is None or rules.presence_policy is PresencePolicy.UNVERIFIED:
        return ScenarioObjectiveEvidence(scenario_id, scenario.pool,
            ScenarioObjectiveStatus.NEEDS_SCENARIO_RULES, None,
            PresencePolicy.UNVERIFIED, None)
    if not isinstance(objective, ObjectiveLocation):
        raise TypeError("objective must be ObjectiveLocation")
    if objective.capture_radius_inches != rules.capture_radius_inches:
        raise ValueError("objective radius differs from verified scenario rules")
    from dataclasses import replace
    from configured_profile import ConfiguredProfile
    from profiles import Profile
    # H3-C automatically reads DOMINANT from profiles. For scenarios verified
    # to count only one/model, override the presence at the position layer
    # without changing canonical profiles or their special rules.
    report = assess_objective_endurance(objective, models)
    if rules.presence_policy is PresencePolicy.ONE_PER_MODEL:
        from objective_position_evidence import ObjectiveModelPosition, assess_objective_positions
        def one_each(snapshot):
            original = {m.model_id: m for m in models}
            # The position evidence records eligibility for each model; reuse it.
            entries = tuple(ObjectiveModelPosition(
                model_id=e.model_id, army_id=e.army_id,
                x_inches=original[e.model_id].x_inches,
                y_inches=original[e.model_id].y_inches,
                scenario_eligible=e.eligibility, effective_presence=1,
            ) for e in snapshot.model_evidence)
            return assess_objective_positions(objective, entries)
        report = replace(report, current_snapshot=one_each(report.current_snapshot),
                         scoring_snapshot=one_each(report.scoring_snapshot))
    controlling = (report.scoring_snapshot.controlling_army_id
                   if rules.scoring_at_observed_turn else None)
    return ScenarioObjectiveEvidence(scenario_id, scenario.pool,
        ScenarioObjectiveStatus.EVIDENCE_READY, report,
        rules.presence_policy, controlling)
