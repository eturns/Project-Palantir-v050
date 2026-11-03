
"""
Project Palantír
DEV-080-B6: Rules-aware casting effectiveness.

Author: Edward Turns (Project Lead)

Read-only, uncalibrated casting diagnostic.
"""

from dataclasses import dataclass
from math import fsum

from magic_capability_measurement import (
    measure_magic_casting_potential,
)
from mechanical_magic_spell_profiles import (
    build_profile_magic_casting_evidence,
)


@dataclass(frozen=True)
class MagicCastingEffectiveness:
    profile_id: str
    spell_count: int
    baseline_probability: float | None
    enhanced_probability: float | None
    extra_casting_dice: int
    additional_attempts_per_activation: int
    spell_results: tuple
    evidence_status: str = "conditional_casting_potential"
    dashboard_score: None = None
    scenario_score: None = None


def assess_caster_effectiveness(
    configured_profile,
    *,
    army,
    army_list,
    remaining_will: int | None = None,
) -> MagicCastingEffectiveness:
    """
    Assess one fielded caster under a one-Will
    hypothetical casting benchmark.

    Does not infer targets, opportunities, enemy
    resistance or successful battlefield effects.
    """
    evidence = build_profile_magic_casting_evidence(
        configured_profile,
        army=army,
        army_list=army_list,
        remaining_will=remaining_will,
    )

    active_rules = tuple(
        rule.id for rule in army_list.army_rules
    )

    spell_ids = tuple(sorted({
        option.spell_id
        for option in evidence.spell_options
    }))

    baseline = []
    enhanced = []
    results = []

    for spell_id in spell_ids:
        normal = measure_magic_casting_potential(
            evidence,
            spell_id=spell_id,
            will_spent=1,
        )

        improved = measure_magic_casting_potential(
            evidence,
            spell_id=spell_id,
            will_spent=1,
            verified_rule_ids=active_rules,
        )

        baseline.append(normal.casting_probability)
        enhanced.append(improved.casting_probability)

        results.append((
            spell_id,
            normal.casting_probability,
            improved.casting_probability,
        ))

    count = len(spell_ids)

    return MagicCastingEffectiveness(
        profile_id=evidence.profile_id,
        spell_count=count,
        baseline_probability=(
            fsum(baseline) / count if count else None
        ),
        enhanced_probability=(
            fsum(enhanced) / count if count else None
        ),
        extra_casting_dice=(
            evidence.conditional_extra_casting_dice
        ),
        additional_attempts_per_activation=(
            evidence.conditional_extra_casts_per_opportunity
        ),
        spell_results=tuple(results),
    )