"""DEV-078-ROTN-C2: connect the C1 cast rules to existing magic evidence.

This is an opt-in analysis adapter, not a turn simulator or scoring input.
The caller supplies declarations and any enemy-target identities. The
existing spell-profile report supplies the known available spell repertoire.
"""
from __future__ import annotations

from dataclasses import dataclass

from necromancer_cast_sequence import CastDeclaration, validate_cast_sequence


@dataclass(frozen=True)
class CastSequenceAssessment:
    caster_profile_id: str
    attempted_spell_ids: tuple[str, ...]
    cast_attempts: int
    permitted_cast_attempts: int
    validated: bool
    evidence_status: str = "declared_sequence_only_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def assess_declared_cast_sequence(
    spell_evidence,
    declarations: tuple[CastDeclaration, ...],
    *,
    army_list,
) -> CastSequenceAssessment:
    """Validate declared spell attempts against a profile magic report.

    Only a fully specified *declared* sequence is assessed. This does not
    infer turns, targets, casting successes, Will use, or actual cast frequency.
    A present spell option (including a conditional dice variant) counts once
    as a known power, not as an extra opportunity.
    """
    profile_id = getattr(spell_evidence, "profile_id", None)
    if not isinstance(profile_id, str) or not profile_id:
        raise TypeError("spell_evidence must include a profile_id")
    if not isinstance(declarations, tuple) or not all(
        isinstance(item, CastDeclaration) for item in declarations
    ):
        raise TypeError("declarations must be a tuple of CastDeclaration")
    list_id = getattr(army_list, "id", None)
    if not isinstance(list_id, str) or not list_id:
        raise TypeError("army_list must include an id")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("army_list.army_rules must be a sequence")
    active_ids = frozenset(getattr(rule, "id", None) for rule in rules)
    if not all(isinstance(rule_id, str) and rule_id for rule_id in active_ids):
        raise TypeError("army rules must have nonempty IDs")
    # Guard against wrongly applying a rule from an unrelated army list.
    if list_id != "DG_ROTN":
        active_ids = active_ids - {"DG_POWER_OF_THE_NECROMANCER"}

    options = getattr(spell_evidence, "spell_options", None)
    if not isinstance(options, (tuple, list)):
        raise TypeError("spell_evidence must include spell_options")
    known_spells = {getattr(option, "spell_id", None) for option in options}
    if not all(isinstance(spell_id, str) and spell_id for spell_id in known_spells):
        raise TypeError("spell options must have nonempty spell IDs")
    for declaration in declarations:
        if declaration.spell_id not in known_spells:
            raise ValueError("declared spell is not in the caster's available repertoire")
    validate_cast_sequence(
        declarations,
        caster_profile_id=profile_id,
        active_army_rule_ids=active_ids,
    )
    enhanced = profile_id == "DG_NEC" and "DG_POWER_OF_THE_NECROMANCER" in active_ids
    return CastSequenceAssessment(
        caster_profile_id=profile_id,
        attempted_spell_ids=tuple(d.spell_id for d in declarations),
        cast_attempts=len(declarations),
        permitted_cast_attempts=2 if enhanced else 1,
        validated=True,
    )
