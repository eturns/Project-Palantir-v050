"""DEV-078-ROTN-D4: Will-funded Necromancer casting evidence.

Author: Edward Turns (Project Lead)

Small, opt-in adapter over the existing mechanical_magic_casting primitive.
It neither mutates army resources nor changes production scores. Its caller
must have established army-list eligibility and legal spell/target sequencing.
"""
from __future__ import annotations

from dataclasses import dataclass
from mechanical_magic_casting import MagicCastEvidence, calculate_cast_evidence

RULE_ID = "DG_HIS_SPIRIT"
NECROMANCER_PROFILE_ID = "DG_NEC"


@dataclass(frozen=True)
class FundedCastRequest:
    spell_id: str
    target_id: str | None
    cast_value: int
    will_spent: int


@dataclass(frozen=True)
class FundedCastResult:
    request: FundedCastRequest
    cast: MagicCastEvidence
    will_before: int
    will_after: int


@dataclass(frozen=True)
class FreeWillSequenceEvidence:
    profile_id: str
    rule_id: str | None
    initial_will: int
    remaining_will: int
    casts: tuple[FundedCastResult, ...]
    evidence_status: str = "explicit_cast_sequence_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def assess_necromancer_funded_casts(
    *,
    profile_id: str,
    active_army_rule_ids: tuple[str, ...] | list[str] | frozenset[str],
    initial_will: int,
    requests: tuple[FundedCastRequest, ...] | list[FundedCastRequest],
) -> FreeWillSequenceEvidence:
    """Evaluate up to two *declared* Will-funded casting attempts.

    The extra die is granted only for DG_NEC with DG_HIS_SPIRIT active.
    Two attempts require DG_POWER_OF_THE_NECROMANCER. Repeated spells and
    repeated non-None target IDs are prohibited on double casts. Zero-Will
    attempts are intentionally unsupported by the underlying general-purpose
    casting model. This is not a battlefield turn simulation.
    """
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise TypeError("profile_id must be a nonblank string")
    if isinstance(initial_will, bool) or not isinstance(initial_will, int):
        raise TypeError("initial_will must be an integer")
    if initial_will < 0:
        raise ValueError("initial_will cannot be negative")
    if not isinstance(active_army_rule_ids, (tuple, list, frozenset)) or any(
        not isinstance(rule, str) for rule in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a sequence of strings")
    if not isinstance(requests, (tuple, list)) or any(
        not isinstance(request, FundedCastRequest) for request in requests
    ):
        raise TypeError("requests must be a sequence of FundedCastRequest")

    ids = frozenset(active_army_rule_ids)
    necromancer = profile_id == NECROMANCER_PROFILE_ID
    max_casts = 2 if necromancer and "DG_POWER_OF_THE_NECROMANCER" in ids else 1
    if len(requests) > max_casts:
        raise ValueError("too many casting attempts for this caster and army list")
    if len(requests) == 2:
        if requests[0].spell_id == requests[1].spell_id:
            raise ValueError("Necromancer cannot cast the same spell twice")
        if (requests[0].target_id is not None and
                requests[0].target_id == requests[1].target_id):
            raise ValueError("Necromancer cannot target the same enemy twice")

    rule_applies = necromancer and RULE_ID in ids
    will = initial_will
    results = []
    for request in requests:
        if not isinstance(request.spell_id, str) or not request.spell_id.strip():
            raise ValueError("spell_id must be nonblank")
        if request.target_id is not None and (
            not isinstance(request.target_id, str) or not request.target_id.strip()
        ):
            raise ValueError("target_id must be None or a nonblank string")
        cast = calculate_cast_evidence(
            cast_value=request.cast_value,
            will_available=will,
            will_spent=request.will_spent,
            additional_dice=1 if rule_applies else 0,
            extra_dice_source=RULE_ID if rule_applies else None,
        )
        results.append(FundedCastResult(request, cast, will, cast.will_remaining_after_attempt))
        will = cast.will_remaining_after_attempt
    return FreeWillSequenceEvidence(
        profile_id=profile_id, rule_id=RULE_ID if rule_applies else None,
        initial_will=initial_will, remaining_will=will,
        casts=tuple(results),
    )
