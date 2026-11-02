"""DEV-078-AH-C2: real-army Pale Orc's Demands Courage diagnostic.

Author: Edward Turns (Project Lead)
Attacker eligibility comes from the imported FieldedModel. Battlefield
position/target Terror remain explicitly supplied. No scoring changes.
"""
from dataclasses import dataclass
from army import Army
from profile_classification import HeroicStatus
from pale_orcs_demands import (
    ARMY_ID, RULE_ID, calculate_pale_orcs_demands,
)

@dataclass(frozen=True)
class PaleOrcsDemandsRequest:
    attacker_model_id: str
    charging_enemy_with_terror: bool
    nearest_friendly_hero_distance_inches: float | None
    other_courage_roll_modifier: int = 0


def build_pale_orcs_demands_evidence(army: Army, army_list, *, request: PaleOrcsDemandsRequest):
    if not isinstance(army, Army):
        raise TypeError("A real Army is required")
    if not isinstance(request, PaleOrcsDemandsRequest):
        raise TypeError("request must be PaleOrcsDemandsRequest")
    if getattr(army_list, "id", None) != ARMY_ID:
        raise ValueError("Pale Orc's Demands requires Azog's Hunters")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("Registered army_rules are required")
    ids = tuple(getattr(rule, "id", None) for rule in rules)
    if any(not isinstance(rule_id, str) or not rule_id.strip() for rule_id in ids):
        raise ValueError("Invalid army rule identifier")
    if RULE_ID not in ids:
        raise ValueError("The Pale Orc's Demands is not registered")
    if not isinstance(request.attacker_model_id, str) or not request.attacker_model_id.strip():
        raise ValueError("A fielded attacker model ID is required")
    matches = [m for m in army.fielded_models() if m.id == request.attacker_model_id]
    if len(matches) != 1:
        raise ValueError("Attacker is not uniquely fielded")
    model = matches[0]
    if model.configured_profile is None:
        raise ValueError("Attacker needs a configured profile")
    profile = model.configured_profile.profile
    is_orc_warrior = (
        profile.heroic_status is HeroicStatus.WARRIOR
        and "ORC" in {str(r).upper() for r in profile.races}
    )
    return calculate_pale_orcs_demands(
        combatant=model.configured_profile,
        army_list_id=army_list.id,
        active_army_rule_ids=ids,
        is_friendly_orc_warrior=is_orc_warrior,
        charging_enemy_with_terror=request.charging_enemy_with_terror,
        nearest_friendly_hero_distance_inches=request.nearest_friendly_hero_distance_inches,
        other_courage_roll_modifier=request.other_courage_roll_modifier,
    )
