"""Project Palantír — web result mapping.

DEV-079-A3-2 / DEV-082-A3-2J-2 / DEV-082-A3-2J-3
Author: Edward Turns (Project Lead)

Preserve the v1 response and historical metrics. Per-upload diagnostics are
optional and never recompute or overwrite calibrated/scenario values.
"""
import json

from web.backend.offence_upload_diagnostic_adapter import (
    build_uploaded_army_offence_api_evidence,
)


def build_web_analysis_result(view: dict) -> dict:
    """Build serializable v1 response with optional, validated Offence data."""
    if not isinstance(view, dict):
        raise TypeError("Analysis view must be a dictionary")
    fields = (
        "army_name", "total_points", "points_limit", "model_count",
        "might", "will", "fate", "key_models", "is_legal",
        "legality_issues", "metrics", "strengths", "weaknesses",
        "scenarios", "evidence", "defence_presentation",
        "provisional_capabilities", "provisional_evidence_reasons",
        "provisional_magic",
    )
    required = (
        "army_name", "total_points", "metrics", "scenarios",
        "provisional_capabilities",
    )
    for key in required:
        if key not in view:
            raise ValueError(f"Missing analysis field: {key}")
    analysis = {key: view[key] for key in fields if key in view}
    if "provisional_offence" in view:
        analysis["provisional_offence"] = build_uploaded_army_offence_api_evidence(
            view["provisional_offence"]
        )
    return json.loads(json.dumps({
        "schema_version": "palantir-web-analysis-v1",
        "analysis": analysis,
    }, allow_nan=False))
