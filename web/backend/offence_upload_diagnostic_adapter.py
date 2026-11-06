"""Project Palantír — DEV-082-A3-2J-3 upload-status JSON adapter.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

This adapter handles only unqualified uploaded-army evidence. The existing
DEV-082-A3-2J-2 adapter remains authoritative for qualified presentation.
"""
from __future__ import annotations

from web.backend.offence_diagnostic_adapter import build_provisional_offence_api_evidence

_ALLOWED_REASONS = {
    "invalid_army", "empty_army", "analysis_limit_exceeded",
    "unsupported_or_unverified_configuration",
}


def build_uploaded_army_offence_api_evidence(evidence: dict) -> dict:
    """Serialize either a previously qualified J-1 row or safe J-3 nulls."""
    if not isinstance(evidence, dict):
        raise ValueError("Offence evidence must be a qualified record")
    if evidence.get("stage") == "DEV-082-A3-2J-1":
        return build_provisional_offence_api_evidence(evidence)
    if (evidence.get("stage") != "DEV-082-A3-2J-3"
            or evidence.get("status") != "not_qualified"
            or evidence.get("reason_code") not in _ALLOWED_REASONS
            or evidence.get("army_key") != "user_upload"
            or evidence.get("neutral_melee") is not None
            or evidence.get("conditional_capabilities") is not None
            or evidence.get("candidate_raw_density") is not None
            or evidence.get("scenario_score") is not None
            or evidence.get("dashboard_score") is not None
            or evidence.get("production_scoring_changed") is not False
            or evidence.get("calibration_changed") is not False
            or evidence.get("promotion_authorised") is not False):
        raise ValueError("Unqualified Offence evidence is not safe for API")
    models = evidence.get("models")
    if models is not None and (type(models) is not int or models < 0):
        raise ValueError("Invalid model count")
    return {
        "stage": "DEV-082-A3-2J-3",
        "status": "not_qualified",
        "reason_code": evidence["reason_code"],
        "visibility": "diagnostic_not_calibrated_not_overall_offence",
        "army_key": "user_upload",
        "models": models,
        "neutral_melee": None,
        "conditional_capabilities": None,
        "safeguards": {
            "candidate_raw_density": None,
            "production_scoring_changed": False,
            "calibration_changed": False,
            "scenario_score": None,
            "dashboard_score": None,
            "promotion_authorised": False,
        },
    }
