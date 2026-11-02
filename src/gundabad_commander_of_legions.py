"""DEV-078-AoG-B1: Commander of Legions standalone entitlement.

Author: Edward Turns (Project Lead)
The 2024 Army of Gundabad grants Master of Battle (5+) ONLY to its
General, and only if that General is Azog or Bolg. This evidence does
not simulate Heroic Actions or apply legacy calibration changes.
"""
from dataclasses import dataclass

ARMY_LIST_ID = "GUNDABAD"
ARMY_RULE_ID = "GUNDABAD_COMMANDER_OF_LEGIONS"
MASTER_OF_BATTLE_RULE_ID = "MASTER_OF_BATTLE"
GENERAL_PROFILE_IDS = frozenset({"AZOG_THE_DEFILER", "BOLG_SPAWN_OF_AZOG"})


@dataclass(frozen=True)
class CommanderOfLegionsEvidence:
    granted: bool
    granted_rule_id: str | None
    master_of_battle_target: int | None
    source_army_rule_id: str | None
    status: str = "conditional_entitlement_only_not_heroic_action_simulation"
    dashboard_score: None = None
    scenario_score: None = None


def resolve_commander_of_legions(
    *,
    army_list_id: str,
    active_army_rule_ids: tuple[str, ...] | list[str] | set[str] | frozenset[str],
    general_profile_id: str | None,
    evaluated_profile_id: str,
    evaluated_model_is_general: bool,
) -> CommanderOfLegionsEvidence:
    """Resolve entitlement for an explicitly identified fielded model.

    A known General identity is required; unknown is never silently treated
    as Azog or Bolg. A Profile's presence does not make it the General.
    """
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be nonblank")
    if not isinstance(active_army_rule_ids, (tuple, list, set, frozenset)):
        raise TypeError("active_army_rule_ids must be a collection")
    if any(not isinstance(x, str) or not x.strip() for x in active_army_rule_ids):
        raise ValueError("army rule IDs must be nonblank strings")
    if general_profile_id is not None and (
        not isinstance(general_profile_id, str) or not general_profile_id.strip()
    ):
        raise ValueError("general_profile_id must be nonblank or None")
    if not isinstance(evaluated_profile_id, str) or not evaluated_profile_id.strip():
        raise ValueError("evaluated_profile_id must be nonblank")
    if type(evaluated_model_is_general) is not bool:
        raise TypeError("evaluated_model_is_general must be boolean")
    if evaluated_model_is_general and general_profile_id is not None and (
        evaluated_profile_id != general_profile_id
    ):
        raise ValueError("evaluated General and declared General profile disagree")
    granted = bool(
        army_list_id == ARMY_LIST_ID
        and ARMY_RULE_ID in active_army_rule_ids
        and evaluated_model_is_general
        and general_profile_id in GENERAL_PROFILE_IDS
        and evaluated_profile_id == general_profile_id
    )
    return CommanderOfLegionsEvidence(
        granted=granted,
        granted_rule_id=MASTER_OF_BATTLE_RULE_ID if granted else None,
        master_of_battle_target=5 if granted else None,
        source_army_rule_id=ARMY_RULE_ID if granted else None,
    )
