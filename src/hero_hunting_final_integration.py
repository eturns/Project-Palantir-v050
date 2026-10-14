"""G4-B: read-only consistency and scoring-isolation gate for Hero Hunting.

No battle legality, optimisation, or scoring is inferred by this validation.
"""
from dataclasses import dataclass
from army import Army
from hero_hunting_real_roster import collect_real_army_roster
from hero_hunting_real_opportunities import collect_real_attack_opportunities
from hero_hunting_real_evidence_report import report_real_army_hero_hunting
from hero_hunting_coverage_audit import audit_hero_hunting_coverage
from hero_hunting_army_capability import ExplainedArmyCapability


@dataclass(frozen=True)
class FinalHeroHuntingIntegration:
    army_label: str
    model_count: int
    capability_count: int
    unresolved_condition_count: int
    conditional_plan_attached: bool
    conditional_target_count: int
    status: str = 'validated_diagnostic_not_battlefield_executable'
    dashboard_score: None = None
    scenario_score: None = None
    combined_elimination_probability: None = None


def validate_hero_hunting_integration(
    label: str,
    army: Army,
    declared_plan: ExplainedArmyCapability | None = None,
    *,
    actor_id_map: dict[str, str] | None = None,
) -> FinalHeroHuntingIntegration:
    """Verify identity, coverage, plan-resource constraints and no score leakage."""
    roster = collect_real_army_roster(label, army)
    inventory = collect_real_attack_opportunities(label, army)
    evidence = report_real_army_hero_hunting(
        label, army, declared_plan, actor_id_map=actor_id_map,
    )
    audit = audit_hero_hunting_coverage(label, army)
    ids = {m.model_id for m in roster.models}
    if len(ids) != len(roster.models):
        raise ValueError('Duplicate imported model identity')
    if len(evidence.models) != len(roster.models) or audit.model_count != len(roster.models):
        raise ValueError('Model counts disagree across diagnostic modules')
    if {m.model_id for m in evidence.models} != ids:
        raise ValueError('Diagnostic model identities differ')
    if any(c.model_id not in ids for c in inventory.capabilities):
        raise ValueError('Capability references an unrecognised real model')
    if sum(m.capability_count for m in evidence.models) != len(inventory.capabilities):
        raise ValueError('Capability totals disagree across diagnostic modules')
    if audit.candidate_count != len(inventory.capabilities):
        raise ValueError('Coverage audit and inventory disagree')
    if audit.verified_executable_attacks != 0:
        raise ValueError('Inventory was incorrectly promoted to executable attacks')
    if evidence.points != roster.total_points or evidence.points != army.total_points():
        raise ValueError('Army points are inconsistent')
    if declared_plan is not None:
        resources = declared_plan.remaining_resources
        resource_ids = [row[0] for row in resources]
        if len(set(resource_ids)) != len(resource_ids):
            raise ValueError('Duplicate resource model in declared plan')
        if any(len(row) != 4 or any(type(n) is not int or n < 0 for n in row[1:]) for row in resources):
            raise ValueError('Invalid remaining resource allocation')
        if declared_plan.dashboard_score is not None or declared_plan.scenario_score is not None:
            raise ValueError('Declared plan has scoring contamination')
        if declared_plan.any_target_elimination_probability is not None:
            raise ValueError('Unsupported joint probability in declared plan')
        if len({t.target_id for t in declared_plan.targets}) != len(declared_plan.targets):
            raise ValueError('Duplicate plan target identity')
    if any(item.dashboard_score is not None or item.scenario_score is not None
           for item in (inventory, evidence, audit)):
        raise ValueError('Mechanical diagnostic changed scoring')
    if evidence.any_target_elimination_probability is not None or audit.any_hero_elimination_probability is not None:
        raise ValueError('Unsupported combined elimination probability')
    unresolved = set(audit.unresolved_requirements)
    return FinalHeroHuntingIntegration(
        army_label=label,
        model_count=len(roster.models),
        capability_count=len(inventory.capabilities),
        unresolved_condition_count=len(unresolved),
        conditional_plan_attached=evidence.conditional_plan_attached,
        conditional_target_count=len(evidence.plan_target_statuses),
    )
