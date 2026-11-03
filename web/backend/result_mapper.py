"""Project Palantír — web result mapping.

DEV-079-A3-2
Author: Edward Turns (Project Lead)

Convert established desktop presentation data into a
JSON-compatible response without recalculating scores.
"""

import json


def build_web_analysis_result(view: dict) -> dict:
    """Build a serializable, versioned web response."""

    if not isinstance(view, dict):
        raise TypeError("Analysis view must be a dictionary")

    fields = (
        "army_name",
        "total_points",
        "points_limit",
        "model_count",
        "might",
        "will",
        "fate",
        "key_models",
        "is_legal",
        "legality_issues",
        "metrics",
        "strengths",
        "weaknesses",
        "scenarios",
        "evidence",
        "defence_presentation",
        "provisional_capabilities",
        "provisional_evidence_reasons",
    )

    required = (
        "army_name",
        "total_points",
        "metrics",
        "scenarios",
        "provisional_capabilities",
    )

    for key in required:
        if key not in view:
            raise ValueError(f"Missing analysis field: {key}")

    result = {
        "schema_version": "palantir-web-analysis-v1",
        "analysis": {
            key: view[key]
            for key in fields
            if key in view
        },
    }

    # Convert tuples into JSON arrays and reject
    # non-finite values or unsupported Python objects.
    return json.loads(
        json.dumps(result, allow_nan=False)
    )
