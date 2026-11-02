"""DEV-078-PITS-D1 — Wizard Hunters, standalone diagnostic mechanic.

Author: Edward Turns (Project Lead)

Uses the established wound table and modifier calculator. Entitlement and
target characteristics are *declared* for a single Strike; this module never
infers that a model can cast spells from Will or magical resistance.
No legacy scores are modified.
"""
from dataclasses import dataclass
from fractions import Fraction

from wound_table import get_wound_target
from wound_modifier import WoundModifier
from wound_probability import get_wound_probability, get_modified_wound_probability

PITS_ARMY_ID = "DG_PITS"
WIZARD_HUNTERS_RULE_ID = "DG_WIZARD_HUNTERS"


@dataclass(frozen=True)
class WizardHuntersEvidence:
    entitled: bool
    applied_modifier: int
    baseline_wound_probability: Fraction
    modified_wound_probability: Fraction
    source_rule_id: str | None
    evidence_status: str = "declared_strike_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_wizard_hunters_strike(
    *,
    army_list_id: str,
    active_army_rule_ids: tuple[str, ...],
    attacker_is_friendly: bool,
    attacker_is_orc: bool,
    attacker_is_warrior: bool,
    defender_is_enemy: bool,
    defender_can_cast_magical_powers: bool,
    is_melee_strike: bool,
    attacker_strength: int,
    defender_defence: int,
) -> WizardHuntersEvidence:
    """Calculate a declared Strike; eligibility is deliberately explicit."""
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be nonblank")
    if not isinstance(active_army_rule_ids, tuple) or any(
        not isinstance(r, str) or not r.strip() for r in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a tuple of rule IDs")
    for name, value in (
        ("attacker_is_friendly", attacker_is_friendly),
        ("attacker_is_orc", attacker_is_orc),
        ("attacker_is_warrior", attacker_is_warrior),
        ("defender_is_enemy", defender_is_enemy),
        ("defender_can_cast_magical_powers", defender_can_cast_magical_powers),
        ("is_melee_strike", is_melee_strike),
    ):
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be a boolean")
    target = get_wound_target(strength=attacker_strength, defence=defender_defence)
    baseline = get_wound_probability(target)
    eligible = all((
        army_list_id == PITS_ARMY_ID,
        WIZARD_HUNTERS_RULE_ID in active_army_rule_ids,
        attacker_is_friendly,
        attacker_is_orc,
        attacker_is_warrior,
        defender_is_enemy,
        defender_can_cast_magical_powers,
        is_melee_strike,
    ))
    modifier = 1 if eligible else 0
    return WizardHuntersEvidence(
        entitled=eligible,
        applied_modifier=modifier,
        baseline_wound_probability=baseline,
        modified_wound_probability=get_modified_wound_probability(
            target, WoundModifier(to_wound=modifier)
        ),
        source_rule_id=WIZARD_HUNTERS_RULE_ID if eligible else None,
    )
