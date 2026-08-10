"""
Project Palantír
================

File:
    profile_metrics.py

Purpose:
    Calculates battlefield ability metrics for a Profile.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-019 – Profile Metrics
"""

# ============================================================================
# Imports
# ============================================================================

from profiles import Profile

from battlefield_evidence import BattlefieldEvidence
from battlefield_profile_evidence_builder import (
    build_profile_battlefield_evidence,
)

from ability_queries import calculate_tag_score

from profile_metrics_entity import ProfileMetrics

from army_analysis_context import ArmyAnalysisContext
from spell_probability import casting_probability
# ============================================================================
# Private Functions
# ============================================================================

def calculate_metric(
    evidence: BattlefieldEvidence,
    metric_id: str,
    profile: Profile,
    context: ArmyAnalysisContext | None,
) -> float:
    """
    Calculates a single battlefield metric.
    """

    return calculate_tag_score(
    evidence.available_abilities(),
    metric_id,
    spell_multiplier_resolver=(
        lambda assignment: _resolve_spell_multiplier(
            assignment,
            profile,
            context,
        )
    ),
    special_rule_multiplier_resolver=(
        lambda assignment: _resolve_special_rule_multiplier(
            assignment,
            metric_id,
        )
    ),
)

def _resolve_special_rule_multiplier(
    assignment,
    metric_id: str,
) -> float:
    """
    Applies parameter-based and army-level handling
    to special rules.
    """

    if (
        assignment.rule.id == "TERROR"
        and metric_id in {
            "COURAGE",
            "CONTROL",
        }
    ):
        return 0.0

    if (
        assignment.rule.id == "HARBINGER_OF_EVIL"
        and metric_id == "COURAGE"
    ):
        return 0.0

    if (
        assignment.rule.id == "SPIDER_WEBS"
        and metric_id == "CONTROL"
    ):
        return 0.0

    if (
        assignment.rule.id == "DOMINANT"
        and metric_id == "OBJECTIVE"
        and assignment.parameter is not None
    ):
        return assignment.parameter ** 0.5

    return 1.0
   
# ============================================================================
# Public Functions
# ============================================================================

def _resolve_spell_multiplier(
    assignment,
    profile: Profile,
    context: ArmyAnalysisContext | None,
) -> float:
    """
    Returns the casting reliability multiplier for a spell
    assignment in the current army-analysis context.
    """

    extra_casting_dice = 0

    if context is not None:
        extra_casting_dice = (
            context.extra_casting_dice_by_profile_id.get(
                profile.id,
                0,
            )
        )

    extra_spell_casts = 0

    if context is not None:
        extra_spell_casts = (
            context.extra_spell_casts_by_profile_id.get(
                profile.id,
                0,
            )
        )

    dice_count = 1 + extra_casting_dice

    spell_casts = 1 + extra_spell_casts

    probability = casting_probability(
        assignment.cast_value,
        dice_count,
    )

    return probability * spell_casts


def _calculate_spellcasting_power(
    profile: Profile,
    context: ArmyAnalysisContext | None,
) -> float:
    """
    Calculates a profile's dedicated Magic contribution
    from its spellcasting capability.
    """

    if not profile.spells:
        return 0.0

    extra_casting_dice = 0
    extra_spell_casts = 0

    if context is not None:
        extra_casting_dice = (
            context.extra_casting_dice_by_profile_id.get(
                profile.id,
                0,
            )
        )

        extra_spell_casts = (
            context.extra_spell_casts_by_profile_id.get(
                profile.id,
                0,
            )
        )

    dice_count = 1 + extra_casting_dice
    spell_casts = 1 + extra_spell_casts

    total_reliability = 0.0

    will_factor = 1 + (
        (profile.will ** 0.5) - 1
    ) / 4

    for assignment in profile.spells:
        total_reliability += casting_probability(
            assignment.cast_value,
            dice_count,
        )

    average_reliability = (
        total_reliability
        / len(profile.spells)
    )

    repertoire_factor = len(
        profile.spells,
    ) ** 0.5

    return (
        average_reliability
        * spell_casts
        * repertoire_factor
        * will_factor
    )

def calculate_profile_metrics(
    profile: Profile,
    context: ArmyAnalysisContext | None = None,
) -> ProfileMetrics:
    """
    Calculates all battlefield metrics for a Profile.
    """

    evidence = build_profile_battlefield_evidence(
        profile,
    )

    return ProfileMetrics(
        offence=calculate_metric(
            evidence,
            "OFFENCE",
            profile,
            context,
        ),
        defence=calculate_metric(
            evidence,
            "DEFENCE",
            profile,
            context,
        ),
        mobility=calculate_metric(
            evidence,
            "MOBILITY",
            profile,
            context,
        ),
        magic=(
            calculate_metric(
                evidence,
                "MAGIC",
                profile,
                context,
            )
            + _calculate_spellcasting_power(
                profile,
                context,
            )
        ),
        shooting=calculate_metric(
            evidence,
            "SHOOTING",
            profile,
            context,
        ),
        courage=calculate_metric(
            evidence,
            "COURAGE",
            profile,
            context,
        ),
        control=calculate_metric(
            evidence,
            "CONTROL",
            profile,
            context,
        ),
        command=calculate_metric(
            evidence,
            "COMMAND",
            profile,
            context,
        ),
        objective=calculate_metric(
            evidence,
            "OBJECTIVE",
            profile,
            context,
        ),
        hero_hunting=calculate_metric(
            evidence,
            "HERO_HUNTING",
            profile,
            context,
        ),
    )