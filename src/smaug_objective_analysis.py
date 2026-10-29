"""DEV-077-SMAUG-D3: production rule-gated, unscored objective evidence.
Edward Turns (Project Lead).
"""
from dataclasses import dataclass
from army import Army
from smaug_sheer_dominance import evaluate_smaug_sheer_dominance


@dataclass(frozen=True)
class SmaugObjectiveEvidence:
    fielded_model_id: str
    rule_present: bool
    status: str
    diagnostic: object
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_objective_evidence(army: Army) -> SmaugObjectiveEvidence | None:
    if not isinstance(army, Army):
        raise TypeError("Smaug objective evidence requires an Army")
    smaugs = [m for m in army.fielded_models() if m.counts_as_model
              and m.profile_id == "SMAUG"]
    if not smaugs:
        return None
    if len(smaugs) != 1:
        raise ValueError("Expected exactly one fielded Smaug")
    model = smaugs[0]
    rules = frozenset(a.rule.id for a in
                      model.configured_profile.effective_special_rules)
    diagnostic = evaluate_smaug_sheer_dominance(
        profile_id=model.profile_id,
        rule_ids=rules,
        distance_to_objective_inches=None,
        objective_range_inches=None,
    )
    return SmaugObjectiveEvidence(
        fielded_model_id=model.id,
        rule_present=diagnostic.rule_present,
        status=diagnostic.status,
        diagnostic=diagnostic,
    )
