"""DEV-077S-I2-G4-A: audited Hero Hunting coverage and closure gates.

This is a coverage contract, not a combat calculation or scoring change.
"""
from dataclasses import dataclass
from army import Army
from hero_hunting_real_evidence_report import report_real_army_hero_hunting
from hero_hunting_real_opportunities import collect_real_attack_opportunities

@dataclass(frozen=True)
class HeroHuntingCoverageAudit:
    army_label: str
    model_count: int
    supported_method_inventory: tuple[str, ...]
    candidate_count: int
    verified_executable_attacks: int
    unresolved_requirements: tuple[str, ...]
    outstanding_boundaries: tuple[str, ...]
    status: str = "mechanical_diagnostics_conditional_battlefield_unverified"
    dashboard_score: None = None
    scenario_score: None = None
    any_hero_elimination_probability: None = None

# Reviewed implementation boundaries. Each deliberately remains visible in G4.
_BOUNDARIES = (
    "attack_candidate_is_not_executable_opportunity",
    "battlefield_position_and_turn_state_not_inferred",
    "declared_plan_probability_is_conditional",
    "no_joint_elimination_probability",
    "no_auto_optimised_multi_target_plan",
    "unrecognised_ranged_wargear_not_proven_complete",
    "siege_engines_require_separate_mechanics",
    "no_calibrated_dashboard_or_scenario_scoring",
)

def audit_hero_hunting_coverage(label: str, army: Army) -> HeroHuntingCoverageAudit:
    """Audit actual evidence surfaces; never turn inventory into live attacks."""
    report = report_real_army_hero_hunting(label, army)
    inventory = collect_real_attack_opportunities(label, army)
    if len({m.model_id for m in report.models}) != len(report.models):
        raise ValueError("Duplicate model identities in report")
    model_ids = {m.model_id for m in report.models}
    if any(c.model_id not in model_ids for c in inventory.capabilities):
        raise ValueError("Capability references unknown model")
    if report.conditional_plan_attached:
        raise ValueError("Coverage audit must use an unallocated real-army report")
    if report.dashboard_score is not None or report.scenario_score is not None:
        raise ValueError("Scoring contamination in real-army report")
    methods = tuple(sorted({c.method for c in inventory.capabilities}))
    if set(methods) - {"melee", "shooting", "magic"}:
        raise ValueError("Unknown attack method")
    requirements = set(inventory.unresolved)
    for c in inventory.capabilities:
        if c.capability_status not in ("identified_not_executable", "incomplete_weapon_profile"):
            raise ValueError("Unexpected executable or unknown capability status")
        if not c.unresolved_conditions:
            raise ValueError("Attack candidate missing battlefield conditions")
        requirements.update(c.unresolved_conditions)
    return HeroHuntingCoverageAudit(
        army_label=report.army_label,
        model_count=len(report.models),
        supported_method_inventory=methods,
        candidate_count=len(inventory.capabilities),
        verified_executable_attacks=0,
        unresolved_requirements=tuple(sorted(requirements)),
        outstanding_boundaries=_BOUNDARIES,
    )
