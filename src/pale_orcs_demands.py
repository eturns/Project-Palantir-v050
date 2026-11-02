"""DEV-078-AH-C1 — The Pale Orc's Demands, standalone Courage diagnostic.

Author: Edward Turns (Project Lead)
The caller supplies confirmed eligibility, the nearest friendly Hero distance,
and the Terror-charge context. Uses Palantir's canonical 2D6 Courage resolver.
No positional or scenario assumptions and no calibration changes.
"""
from dataclasses import dataclass
from fractions import Fraction
from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext, calculate_courage_test_success_probability

ARMY_ID = "AZOGS_HUNTERS"
RULE_ID = "DG_PALE_ORCS_DEMANDS"

@dataclass(frozen=True)
class PaleOrcsDemandsEvidence:
    entitled: bool
    bonus: int
    baseline_pass_probability: Fraction
    modified_pass_probability: Fraction
    source_rule_id: str | None
    status: str = "declared_terror_charge_context_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_pale_orcs_demands(
    *,
    combatant: ConfiguredProfile,
    army_list_id: str,
    active_army_rule_ids: tuple[str, ...],
    is_friendly_orc_warrior: bool,
    charging_enemy_with_terror: bool,
    nearest_friendly_hero_distance_inches: int | float | None,
    other_courage_roll_modifier: int = 0,
) -> PaleOrcsDemandsEvidence:
    """Evaluate a declared test. None distance means no confirmed nearby Hero."""
    if not isinstance(combatant, ConfiguredProfile):
        raise TypeError("combatant must be ConfiguredProfile")
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be nonblank")
    if not isinstance(active_army_rule_ids, tuple) or any(
        not isinstance(x, str) or not x.strip() for x in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a tuple of nonblank IDs")
    for name, value in (("is_friendly_orc_warrior",is_friendly_orc_warrior),
                        ("charging_enemy_with_terror",charging_enemy_with_terror)):
        if type(value) is not bool:
            raise TypeError(f"{name} must be boolean")
    if type(other_courage_roll_modifier) is not int:
        raise TypeError("other_courage_roll_modifier must be integer")
    if nearest_friendly_hero_distance_inches is not None:
        from math import isfinite
        d=nearest_friendly_hero_distance_inches
        if isinstance(d,bool) or not isinstance(d,(int,float)) or not isfinite(d) or d<0:
            raise ValueError("Hero distance must be a finite nonnegative number")
    eligible = (
        army_list_id == ARMY_ID and RULE_ID in active_army_rule_ids
        and is_friendly_orc_warrior and charging_enemy_with_terror
        and nearest_friendly_hero_distance_inches is not None
        and nearest_friendly_hero_distance_inches <= 6
    )
    bonus=int(eligible)
    base=calculate_courage_test_success_probability(
        combatant, CourageTestContext(roll_modifier=other_courage_roll_modifier)
    )
    modified=calculate_courage_test_success_probability(
        combatant, CourageTestContext(roll_modifier=other_courage_roll_modifier+bonus)
    )
    return PaleOrcsDemandsEvidence(
        entitled=eligible, bonus=bonus,
        baseline_pass_probability=base, modified_pass_probability=modified,
        source_rule_id=RULE_ID if eligible else None,
    )
