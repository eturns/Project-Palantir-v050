"""DEV-077-SMAUG-D5A — unscored production Lust for Gold evidence.

Edward Turns (Project Lead)
No battlefield positions are inferred by standard army analysis.
"""
from dataclasses import dataclass
from army import Army
from smaug_lust_for_gold import assess_lust_for_gold


@dataclass(frozen=True)
class SmaugLustForGoldArmyEvidence:
    fielded_model_id: str
    rule_present: bool
    status: str
    diagnostic: object
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_lust_for_gold_evidence(army: Army) -> SmaugLustForGoldArmyEvidence | None:
    if not isinstance(army, Army):
        raise TypeError("Lust for Gold evidence requires a real Army")
    models = tuple(m for m in army.fielded_models()
                   if m.counts_as_model and m.profile_id == "SMAUG")
    if not models:
        return None
    if len(models) != 1:
        raise ValueError("Expected exactly one fielded Smaug")
    model = models[0]
    rules = frozenset(a.rule.id for a in
                      model.configured_profile.effective_special_rules)
    diagnostic = assess_lust_for_gold(
        profile_id=model.profile_id, rule_ids=rules,
        targets=None, moving=None,
    )
    return SmaugLustForGoldArmyEvidence(
        fielded_model_id=model.id,
        rule_present=diagnostic.rule_present,
        status=diagnostic.status,
        diagnostic=diagnostic,
    )
