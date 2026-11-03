"""
Project Palantír
DEV-080-F5A: Provisional Web Magic Evidence.

Author: Edward Turns (Project Lead)

Builds JSON-compatible Magic evidence from an
already-imported army.

Does not re-import armies, modify the frozen
calibration or change scenario scores.
"""

from army import Army
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)
from army_magic_output_envelope import (
    assess_army_magic_output,
)
from army_magic_resource_projection import (
    assess_army_magic_resources,
)
from magic_casting_delivery_score import (
    calculate_magic_casting_delivery,
)


def build_provisional_magic_web_evidence(
    workflow_result: dict,
) -> dict:
    """
    Reuse the established workflow's army
    and army-list objects.
    """

    if not isinstance(workflow_result, dict):
        raise TypeError(
            "workflow_result must be a dictionary"
        )

    army = workflow_result.get("army")
    army_list = workflow_result.get("army_list")

    if not isinstance(army, Army) or army_list is None:
        raise ValueError(
            "Real imported army and army list required"
        )

    assessment = assess_army_magic_capability(
        army,
        army_list,
    )

    output = assess_army_magic_output(assessment)

    resources = assess_army_magic_resources(
        army,
        assessment,
    )

    delivery = calculate_magic_casting_delivery(
        expected_successes_lower=(
            output.minimum_expected_successes
        ),
        expected_successes_upper=(
            output.maximum_expected_successes
        ),
        modelled_attempts=output.modelled_attempts,
    )

    return {
        "title": "Provisional Casting Delivery",
        "status": delivery.evidence_status,
        "reference_activations": 6,
        "reference_attempts": delivery.reference_attempts,
        "lower_score": delivery.lower_score,
        "upper_score": delivery.upper_score,
        "caster_count": assessment.caster_count,
        "distinct_spell_count": len(
            assessment.distinct_spell_ids
        ),
        "modelled_attempts": output.modelled_attempts,
        "funded_attempts": resources.funded_attempts,
        "expected_successes_lower": (
            output.minimum_expected_successes
        ),
        "expected_successes_upper": (
            output.maximum_expected_successes
        ),
        "temporary_will_spent": (
            resources.temporary_will_spent
        ),
        "permanent_will_spent": (
            resources.permanent_will_spent
        ),
        "permanent_will_remaining": (
            resources.permanent_will_remaining
        ),
        "spell_ids": list(
            assessment.distinct_spell_ids
        ),
        "verified_effect_spell_ids": list(
            assessment.spell_impact_coverage
            .verified_effect_spell_ids
        ),
        "unverified_effect_spell_ids": list(
            assessment.spell_impact_coverage
            .unverified_effect_spell_ids
        ),
        "overall_magic_score": None,
        "display_only": True,
    }
