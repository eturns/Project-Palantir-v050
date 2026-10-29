"""DEV-077-SMAUG-C3C/E: opt-in, uncalibrated incoming missile evidence.

Requires Smaug's actual MISSING_SCALE rule assignment. No inference about
battlefield obstruction or the existing Defence/hero-hunting scores.
"""
from dataclasses import dataclass

from army import Army
from defensive_state import DefensiveState
from smaug_missing_scale_volley import (
    IncomingMissile,
    MissingScaleVolleyEvidence,
    calculate_smaug_missing_scale_volley,
)


@dataclass(frozen=True)
class MissingScaleRequest:
    shooters: tuple[IncomingMissile, ...]
    defensive_state: DefensiveState
    might_for_fate: int = 0


@dataclass(frozen=True)
class SmaugMissingScaleAnalysis:
    status: str
    evidence: MissingScaleVolleyEvidence | None = None
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_missing_scale_analysis(
    army: Army,
    *,
    request: MissingScaleRequest | None = None,
) -> SmaugMissingScaleAnalysis | None:
    """Return conditional incoming-shooting evidence only for eligible Smaug.

    Callers must supply an independently verified shooting context. No claim of
    overall battle survival is made from this isolated incoming volley.
    """
    if not isinstance(army, Army):
        raise TypeError("Missing Scale analysis requires a real Army")
    smaugs = tuple(
        m for m in army.fielded_models()
        if m.counts_as_model and m.configured_profile is not None
        and m.configured_profile.profile.id == "SMAUG"
    )
    if not smaugs:
        if request is not None:
            raise ValueError("Missing Scale request requires Smaug")
        return None
    if len(smaugs) != 1 or army.model_count() != 1:
        raise ValueError("Missing Scale requires a single-model Smaug army")
    profile = smaugs[0].configured_profile
    rules = {assignment.rule.id for assignment in profile.effective_special_rules}
    if "MISSING_SCALE" not in rules:
        if request is not None:
            raise ValueError("Smaug has no MISSING_SCALE rule assignment")
        return SmaugMissingScaleAnalysis("missing_scale_rule_not_registered")
    if request is None:
        return SmaugMissingScaleAnalysis("requires_declared_incoming_shooting")
    if not isinstance(request, MissingScaleRequest):
        raise TypeError("request must be MissingScaleRequest")
    evidence = calculate_smaug_missing_scale_volley(
        target_profile_id="SMAUG",
        shooters=request.shooters,
        state=request.defensive_state,
        defender_might_for_fate=request.might_for_fate,
        target_defence=profile.effective_defence,
    )
    return SmaugMissingScaleAnalysis(
        "conditional_incoming_shooting_evidence_not_ratings", evidence
    )
