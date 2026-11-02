"""DEV-078-AoG-B2 — Commander of Legions production entitlement.

Author: Edward Turns (Project Lead).
General identity comes from imported ArmyDefinition, not Army membership.
No Heroic Action simulation, scoring, or calibration changes.
"""
from dataclasses import dataclass
from army import Army
from gundabad_commander_of_legions import (
    ARMY_LIST_ID, ARMY_RULE_ID, resolve_commander_of_legions
)

@dataclass(frozen=True)
class CommanderOfLegionsArmyEvidence:
    general_profile_id: str
    general_model_id: str
    entitlement: object
    status: str = "imported_general_entitlement_only_not_heroic_action_simulation"
    dashboard_score: None = None
    scenario_score: None = None


def build_commander_of_legions_army_evidence(army: Army, army_list, *,
                                             army_definition):
    if not isinstance(army, Army):
        raise TypeError("Requires a real Army")
    if getattr(army_list, "id", None) != ARMY_LIST_ID:
        raise ValueError("Commander of Legions requires Army of Gundabad")
    if getattr(army_definition, "army_list_id", None) != ARMY_LIST_ID:
        raise ValueError("Imported definition must describe Army of Gundabad")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("Registered army rules required")
    rule_ids = tuple(getattr(r, "id", None) for r in rules)
    if any(not isinstance(r, str) or not r.strip() for r in rule_ids):
        raise ValueError("Malformed army-rule identifier")
    if ARMY_RULE_ID not in rule_ids:
        raise ValueError("Commander of Legions rule not registered")
    general_id = getattr(army_definition, "leader_profile_id", None)
    band_id = getattr(army_definition, "leader_warband_id", None)
    if not isinstance(general_id, str) or not general_id.strip():
        raise ValueError("Imported General identity is required")
    if not isinstance(band_id, str) or not band_id.strip():
        raise ValueError("Imported General warband is required")
    matches = [
        m for m in army.fielded_models()
        if m.profile_id == general_id and m.warband_id == band_id
        and m.configured_profile is not None
    ]
    if len(matches) != 1:
        raise ValueError("Cannot uniquely resolve imported General to fielded model")
    model = matches[0]
    entitlement = resolve_commander_of_legions(
        army_list_id=army_list.id,
        active_army_rule_ids=rule_ids,
        general_profile_id=general_id,
        evaluated_profile_id=model.profile_id,
        evaluated_model_is_general=True,
    )
    return CommanderOfLegionsArmyEvidence(
        general_profile_id=general_id, general_model_id=model.id,
        entitlement=entitlement,
    )
