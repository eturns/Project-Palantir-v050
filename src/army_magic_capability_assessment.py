
"""
Project Palantír
DEV-080-B5: Army-level Magic capability assessment.

Author: Edward Turns (Project Lead)

Read-only diagnostic. No calibrated dashboard score,
scenario changes or optimiser changes.
"""

from dataclasses import dataclass

from army import Army
from mechanical_magic_army_contract import (
    build_army_magic_contract,
)
from mechanical_magic_completeness import (
    audit_army_magic_completeness,
)
from rotn_army_cast_service import (
    build_army_necromancer_cast_evidence,
)
from magic_casting_effectiveness import (
    assess_caster_effectiveness,
)


@dataclass(frozen=True)
class ArmyMagicCapabilityAssessment:
    model_count: int
    caster_count: int
    starting_caster_will: int
    one_will_attempt_ceiling: int
    distinct_spell_ids: tuple[str, ...]
    one_will_probability_weighted_mean: float | None
    spell_effect_categories: tuple[str, ...]
    enhanced_casting_model_ids: tuple[str, ...]
    enhanced_attempts_per_activation: int | None
    caster_effectiveness: tuple

    evidence_status: str = "roster_potential_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def assess_army_magic_capability(
    army: Army,
    army_list,
) -> ArmyMagicCapabilityAssessment:
    """
    Collect existing Magic evidence into one army-level report.

    Casting opportunities, targets, resistance and applied
    spell effects are not inferred.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")

    completeness = audit_army_magic_completeness(army)

    if not completeness.is_complete:
        raise ValueError(
            "Cannot assess Magic with incomplete spell data"
        )

    contract = build_army_magic_contract(army)

    necromancer = build_army_necromancer_cast_evidence(
        army,
        army_list,
    )

    caster_effectiveness = []

    entries_by_model = (
        entry
        for entry in army.entries
        for _ in range(entry.quantity)
    )

    for model, entry in zip(
        army.fielded_models(),
        entries_by_model,
        strict=True,
    ):
        configured = model.configured_profile

        if configured is None:
            continue

        if not configured.profile.spells:
            continue

        effective_will = entry.get_attribute("will")

        if effective_will <= 0:
            # Zero-Will casters cannot fund the
            # one-Will benchmark attempt.
            continue

        assessment = assess_caster_effectiveness(
            configured,
            army=army,
            army_list=army_list,
            remaining_will=effective_will,
        )

        caster_effectiveness.append((
            model.id,
            assessment,
        ))

    enhanced_ids = ()
    enhanced_attempts = None

    if necromancer is not None:
        enhanced_ids = necromancer.eligible_model_ids
        enhanced_attempts = (
            necromancer.permitted_attempts_per_activation
        )

    return ArmyMagicCapabilityAssessment(
        model_count=contract.model_count,
        caster_count=contract.caster_count,
        starting_caster_will=contract.starting_caster_will,
        one_will_attempt_ceiling=(
            contract.one_will_attempt_ceiling
        ),
        distinct_spell_ids=contract.distinct_spell_ids,
        one_will_probability_weighted_mean=(
            contract.one_will_probability_weighted_mean
        ),
        spell_effect_categories=tuple(
            category.tag_id
            for category in contract.effect_categories
        ),
        enhanced_casting_model_ids=enhanced_ids,
        enhanced_attempts_per_activation=enhanced_attempts,
        caster_effectiveness=tuple(caster_effectiveness),
    )
