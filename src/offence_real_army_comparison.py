"""DEV-082-A3-2B: read-only, real-army shadow Offence comparison.

Author: Edward Turns (Project Lead)

Summarises A3-2A evidence for a real imported Army. No inferred charge/trap
frequency, no Might spending, no army-level replacement density, no calibration.
This module is NOT connected to production dashboards or analysis services.
"""
from __future__ import annotations

from collections import Counter
import math


def build_real_army_offence_comparison(army, *, collector=None) -> dict:
    """Collect opt-in shadow evidence and produce a JSON-safe audit report.

    `collector` injection is only for deterministic acceptance testing. By
    default the real A3-2A collector is called with enabled=True.
    Exceptions from unsupported profiles deliberately propagate: nothing
    silently disappears from the comparison or becomes a numerical zero.
    """
    if collector is None:
        from offence_shadow_evidence import collect_shadow_offence_evidence
        collector = collect_shadow_offence_evidence

    if army is None or not callable(getattr(army, "total_points", None)):
        raise TypeError("A real imported Army is required")
    shadow = collector(army, enabled=True)
    if shadow.enabled is not True:
        raise ValueError("Shadow collection was not enabled")
    if shadow.candidate_raw_density is not None or shadow.comparable is not False:
        raise ValueError("A3-2B must not claim an army-wide replacement density")
    raw = shadow.legacy_raw_density
    if type(raw) not in (float, int) or not math.isfinite(raw) or raw < 0:
        raise ValueError("Legacy raw density is missing or invalid")

    points = army.total_points()
    if type(points) not in (float, int) or not math.isfinite(points) or points < 0:
        raise ValueError("Army points are invalid")
    reasons = Counter()
    rows = []
    counted = 0
    for item in shadow.profiles:
        quantity = item.quantity
        if type(quantity) is not int or quantity < 1:
            raise ValueError("Invalid profile quantity")
        if not isinstance(item.profile_id, str) or not item.profile_id.strip():
            raise ValueError("Invalid profile ID")
        probabilities = (
            item.uncharged_probability, item.charged_probability,
            item.cavalry_eligible_probability,
        )
        if any(type(v) not in (int, float) or not math.isfinite(v)
               or not 0 <= v <= 1 for v in probabilities):
            raise ValueError("Invalid conditional probability")
        if item.weighted_probability is not None:
            raise ValueError("Unverified weighted combat probability")
        counted += quantity
        for reason in set(item.unresolved_context):
            reasons[reason] += quantity
        rows.append({
            "profile_id": item.profile_id,
            "quantity": quantity,
            "uncharged_probability": item.uncharged_probability,
            "charged_probability": item.charged_probability,
            "eligible_cavalry_charge_probability": item.cavalry_eligible_probability,
            "unresolved_context": list(item.unresolved_context),
            "evidence_status": item.evidence_status,
        })

    if hasattr(army, "model_count") and callable(army.model_count):
        expected = army.model_count()
        if counted != expected:
            raise ValueError(
                f"Shadow profile quantities ({counted}) do not match "
                f"army model count ({expected})"
            )

    return {
        "stage": "DEV-082-A3-2B",
        "source": "real_imported_army_shadow_offence",
        "army_points": points,
        "fielded_models": counted,
        "legacy_raw_density": raw,
        "reference_raw_density": raw,
        "candidate_raw_density": None,
        "comparable": False,
        "evidence_status": shadow.evidence_status,
        "comparison_reason": shadow.reason,
        "profile_rows": rows,
        "unresolved_model_counts": dict(sorted(reasons.items())),
        "metric_id": "offence_density",
        "target_population": "ordinary_single_wound_benchmark",
        "calibration_changed": False,
        "production_scoring_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
