"""
Project Palantír
DEV-080-F3: Army Magic Resource Projection Adapter.

Author: Edward Turns (Project Lead)

Connects actual model special-rule grants to the
hypothetical six-activation Will projection.

Does not change permanent resources, production
scores, scenarios or optimiser behaviour.
"""

from dataclasses import dataclass

from army import Army
from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from special_rule_temporary_resource_grants import (
    get_special_rule_temporary_resource_grants,
)
from magic_turn_resource_projection import (
    project_magic_resources,
)


@dataclass(frozen=True)
class ArmyMagicResourceProjection:
    caster_results: tuple
    funded_attempts: int
    temporary_will_spent: int
    permanent_will_spent: int
    permanent_will_remaining: int
    evidence_status: str = (
        "conditional_army_resource_projection"
    )
    dashboard_score: None = None
    scenario_score: None = None


def assess_army_magic_resources(
    army: Army,
    magic_assessment,
) -> ArmyMagicResourceProjection:
    """
    Project each evaluated caster independently.

    Assumes one Will per attempt and maximum
    hypothetical casting opportunities.

    All eligible temporary Will is allocated to
    casting in this conditional projection.
    """

    if not isinstance(army, Army):
        raise TypeError("army must be an Army")

    models = {
        model.id: model
        for model in army.fielded_models()
    }

    results = []

    for model_id, capacity in magic_assessment.caster_capacity:
        model = models[model_id]
        configured = model.configured_profile

        rule_ids = frozenset(
            assignment.rule.id
            for assignment in configured.effective_special_rules
        )

        owner = ResourceOwner(
            fielded_model_id=model_id
        )

        grants = get_special_rule_temporary_resource_grants(
            owner,
            rule_ids,
        )

        temporary_will = sum(
            grant.amount
            for grant in grants
            if grant.resource_type == ResourceType.WILL
        )

        turns = capacity.hypothetical_activations
        attempts_per_turn = min(
            capacity.permitted_attempts_per_activation,
            len({
                spell.spell.id
                for spell in configured.profile.spells
            }),
        )

        schedule = (attempts_per_turn,) * turns

        projection = project_magic_resources(
            starting_permanent_will=capacity.starting_will,
            temporary_will_per_turn=temporary_will,
            attempts_by_turn=schedule,
        )

        results.append((model_id, projection))

    return ArmyMagicResourceProjection(
        caster_results=tuple(results),
        funded_attempts=sum(
            item.funded_attempts
            for _, item in results
        ),
        temporary_will_spent=sum(
            item.temporary_will_spent
            for _, item in results
        ),
        permanent_will_spent=sum(
            item.permanent_will_spent
            for _, item in results
        ),
        permanent_will_remaining=sum(
            item.permanent_will_remaining
            for _, item in results
        ),
    )