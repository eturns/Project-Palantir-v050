"""DEV-077-SMAUG-C5D/E — uncalibrated, turn-scoped magic evidence.

Edward Turns (Project Lead)
Separates persistent Will from conditional temporary Will. Does not change
canonical profiles, permanent army resource totals or any scores.
"""
from dataclasses import dataclass

from army import Army
from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from special_rule_temporary_resource_grants import get_special_rule_temporary_resource_grants
from temporary_resource_grant_totals import calculate_temporary_resource_total
from mechanical_magic_spell_profiles import build_profile_magic_casting_evidence


@dataclass(frozen=True)
class SmaugMagicAnalysis:
    profile_id: str
    status: str
    permanent_will: int
    temporary_will_this_turn: int
    hypothetical_available_will: int
    permanent_casting: object
    conditional_casting: object
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_magic_analysis(army: Army) -> SmaugMagicAnalysis | None:
    """Show per-turn casting options, not sustained spell-casting throughput.

    The extra point may be used for other Will expenditures; hypothetical
    casting with all available Will is not a forecast or guaranteed cast.
    """
    if not isinstance(army, Army):
        raise TypeError("Smaug magic analysis requires a real Army")
    models = tuple(m for m in army.fielded_models()
                   if m.counts_as_model and m.configured_profile is not None
                   and m.configured_profile.profile.id == "SMAUG")
    if not models:
        return None
    if len(models) != 1 or army.model_count() != 1:
        raise ValueError("Smaug magic analysis requires a single-model Smaug army")
    model = models[0]
    profile = model.configured_profile
    permanent = profile.profile.will
    if not isinstance(permanent, int) or isinstance(permanent, bool) or permanent < 0:
        raise ValueError("Invalid permanent Will characteristic")
    rule_ids = frozenset(a.rule.id for a in profile.effective_special_rules)
    # The grant is owned by one actual model; the rule engine determines amount.
    owner = ResourceOwner(fielded_model_id=model.id)
    grants = get_special_rule_temporary_resource_grants(owner, rule_ids)
    temporary = calculate_temporary_resource_total(
        grants=grants, owner=owner, resource_type=ResourceType.WILL)
    permanent_options = build_profile_magic_casting_evidence(
        profile, remaining_will=permanent)
    if "DESOLATOR_OF_THE_NORTH" not in rule_ids:
        return SmaugMagicAnalysis(
            "SMAUG", "temporary_will_rule_not_assigned", permanent, 0,
            permanent, permanent_options, None)
    if temporary != 1:
        raise ValueError("Desolator of the North must grant exactly one temporary Will")
    conditional_options = build_profile_magic_casting_evidence(
        profile, remaining_will=permanent + temporary)
    return SmaugMagicAnalysis(
        "SMAUG", "conditional_single_turn_magic_evidence_not_scoring",
        permanent, temporary, permanent + temporary,
        permanent_options, conditional_options)
