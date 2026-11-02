"""DEV-078-AoG-C1 — 'Here ends your filthy bloodline!' standalone evidence.

Author: Edward Turns (Project Lead)

Uses canonical wound-table and reroll consumers; explicit army, attacker,
Erebor target, and melee Strike eligibility. No assumptions about encounter
frequency or calibrated scoring.
"""
from dataclasses import dataclass
from fractions import Fraction

from wound_table import get_wound_target
from wound_probability import (
    get_wound_probability,
    get_wound_probability_with_reroll,
)
from wound_reroll import WoundReroll

ARMY_LIST_ID = "GUNDABAD"
RULE_ID = "GUNDABAD_FILTHY_BLOODLINE"
AZOG_PROFILE_ID = "AZOG_THE_DEFILER"


@dataclass(frozen=True)
class FilthyBloodlineEvidence:
    entitled: bool
    reroll_failed_to_wound: bool
    baseline_wound_probability: Fraction
    modified_wound_probability: Fraction
    source_rule_id: str | None
    status: str = "declared_strike_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_filthy_bloodline_strike(
    *,
    army_list_id: str,
    active_army_rule_ids: tuple[str, ...],
    attacker_profile_id: str,
    attacker_is_friendly: bool,
    defender_is_erebor: bool,
    defender_is_enemy: bool,
    is_melee_strike: bool,
    attacker_strength: int,
    defender_defence: int,
) -> FilthyBloodlineEvidence:
    """Resolve one explicitly declared Strike using shared MESBG probabilities.

    The existing wound probability consumer applies rerolls to each required
    roll, including additional high-Defence To Wound dice. No added modifiers
    or unsupported automatic-success thresholds are inferred here.
    """
    for name, value in (
        ("army_list_id", army_list_id),
        ("attacker_profile_id", attacker_profile_id),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a nonblank string")
    if not isinstance(active_army_rule_ids, tuple) or any(
        not isinstance(rule_id, str) or not rule_id.strip()
        for rule_id in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a tuple of nonblank strings")
    for name, value in (
        ("attacker_is_friendly", attacker_is_friendly),
        ("defender_is_erebor", defender_is_erebor),
        ("defender_is_enemy", defender_is_enemy),
        ("is_melee_strike", is_melee_strike),
    ):
        if type(value) is not bool:
            raise TypeError(f"{name} must be boolean")
    if type(attacker_strength) is not int or type(defender_defence) is not int:
        raise TypeError("Strength and Defence must be integer characteristics")

    target = get_wound_target(attacker_strength, defender_defence)
    baseline = get_wound_probability(target)
    entitled = (
        army_list_id == ARMY_LIST_ID
        and RULE_ID in active_army_rule_ids
        and attacker_profile_id == AZOG_PROFILE_ID
        and attacker_is_friendly
        and defender_is_erebor
        and defender_is_enemy
        and is_melee_strike
    )
    modified = (
        get_wound_probability_with_reroll(target, WoundReroll(reroll_failed=True))
        if entitled else baseline
    )
    return FilthyBloodlineEvidence(
        entitled=entitled,
        reroll_failed_to_wound=entitled,
        baseline_wound_probability=baseline,
        modified_wound_probability=modified,
        source_rule_id=RULE_ID if entitled else None,
    )
