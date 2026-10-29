"""DEV-077-SMAUG-C2D/E: opt-in, uncalibrated Breathe Fire analysis contract.

Battlefield geometry and defenders MUST be supplied. Never infer them from
a roster or silently convert raw evidence into Shooting/Offence ratings.
"""
from dataclasses import dataclass

from army import Army
from smaug_breathe_fire import FireVictim
from smaug_fire_defensive_resolution import FireDefender
from smaug_fire_shooting_evidence import (
    SmaugFireShootingEvidence, calculate_smaug_fire_shooting_evidence,
)


@dataclass(frozen=True)
class SmaugFireRequest:
    target_distance_inches: float
    primary_target_id: str
    victims: tuple[FireVictim, ...]
    defenders: tuple[FireDefender, ...]
    to_hit_modifier: int = 0


@dataclass(frozen=True)
class SmaugFireAnalysisEvidence:
    source_profile_id: str
    status: str
    requests: tuple[SmaugFireShootingEvidence, ...]
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_fire_analysis_evidence(
    army: Army,
    *,
    requests: tuple[SmaugFireRequest, ...] | None = None,
) -> SmaugFireAnalysisEvidence | None:
    if not isinstance(army, Army):
        raise TypeError("Smaug fire evidence requires a real Army")
    smaug = tuple(model for model in army.fielded_models()
                  if model.counts_as_model and model.configured_profile is not None
                  and model.configured_profile.profile.id == "SMAUG")
    if not smaug:
        if requests:
            raise ValueError("Breathe Fire requests require SMAUG in the army")
        return None
    if len(smaug) != 1 or army.model_count() != 1:
        raise ValueError("Smaug fire evidence requires a single-model SMAUG army")
    if requests is None:
        return SmaugFireAnalysisEvidence(
            "SMAUG", "requires_declared_battlefield_targets", ()
        )
    if not isinstance(requests, tuple) or any(
        not isinstance(item, SmaugFireRequest) for item in requests
    ):
        raise TypeError("requests must be a tuple of SmaugFireRequest")
    results = tuple(calculate_smaug_fire_shooting_evidence(
        source_profile_id="SMAUG",
        target_distance_inches=request.target_distance_inches,
        primary_target_id=request.primary_target_id,
        victims=request.victims,
        defenders=request.defenders,
        shoot_value=smaug[0].configured_profile.effective_shooting,
        to_hit_modifier=request.to_hit_modifier,
    ) for request in requests)
    return SmaugFireAnalysisEvidence(
        "SMAUG",
        "conditional_bounded_fire_evidence_not_dashboard_scoring" if results
        else "no_fire_attacks_declared",
        results,
    )
