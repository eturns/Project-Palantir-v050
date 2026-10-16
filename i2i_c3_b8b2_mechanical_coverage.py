"""B8-B2: read-only mechanical coverage assessment for the six reference armies.

A coverage inventory, not a new scoring implementation. Uses B8-B's actual
option audit and the canonical ten-metric provider inventory. Never infers
that an implemented rule is mechanically complete or a numerical zero.
"""
import json

from i2i_c3_b8b_mechanical_qualification import audit as audit_equipment
from unified_capability_inventory import get_capability_inventory, METRIC_NAMES

# The C3 extraction status was established in the prior unified provider audit.
# These are *measurement interface* classifications, not assertions that all
# special rules for every army have been implemented.
MEASUREMENT_STATE = {
    "offence": "available",
    "defence": "available",
    "mobility": "available",
    "magic": "partial",
    "shooting": "available",
    "courage": "available",
    "control": "context_required",
    "command": "context_required",
    "objective": "context_required",
    "hero_hunting": "context_required",
}
REASONS = {
    "magic": "Casting/resource evidence is conditional; no approved full army magic scalar.",
    "control": "Requires target, effect duration, recipient and battle state.",
    "command": "Requires action opportunities, Might state, beneficiaries and timing.",
    "objective": "Requires scenario victory conditions and actual objective positions.",
    "hero_hunting": "Requires named target and engagement/resource assumptions.",
}


def build_report(equipment_report=None):
    if equipment_report is None:
        equipment_report = audit_equipment()
    inventory = {record.metric: record for record in get_capability_inventory()}
    if tuple(inventory) != tuple(METRIC_NAMES):
        raise ValueError("Capability inventory does not match canonical metric order")
    if set(MEASUREMENT_STATE) != set(METRIC_NAMES):
        raise ValueError("Incomplete mechanical measurement status table")
    rows = []
    for entry in equipment_report["results"]:
        ready = entry["status"] == "option_audit_passed"
        metrics = []
        for metric in METRIC_NAMES:
            provider = inventory[metric]
            state = MEASUREMENT_STATE[metric]
            # A covered numerical interface is not proof of per-army completeness.
            final = state if ready else "blocked_by_equipment"
            metrics.append({
                "metric": metric, "measurement_status": final,
                "provider_integration": provider.integration_status,
                "unit": provider.mechanical_unit,
                "limitation": REASONS.get(metric, (
                    "Mechanical measurement interface available; profile-specific "
                    "special rules still require independent approval."
                )),
                "value": None,  # No invented measured values.
                "mechanically_approved": False,
            })
        rows.append({
            "army": entry["army"], "equipment_audit_passed": ready,
            "known_resolved_ranged_models": entry["resolved_shooters"],
            "metric_coverage": metrics,
            "full_profile_mechanics_approved": False,
        })
    return {
        "stage": "B8-B2", "scope": "mechanical_provider_coverage",
        "armies": rows,
        "limitations": [
            "Provider availability is separate from profile-specific completeness.",
            "Shooting has a measurable zero when no armed shooters; unavailable "
            "or context-dependent capabilities must not be assigned zero.",
            "Magic is partial; do not interpret a missing caster as an army "
            "with fully audited zero magical capability.",
            "No scenario, targets, positions or resources were inferred.",
        ],
        "archetype_review_approved": False,
        "full_special_rules_approved": False,
        "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
