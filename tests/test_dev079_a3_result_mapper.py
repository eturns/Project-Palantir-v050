"""DEV-079-A3-2 — web result mapping tests.

Author: Edward Turns (Project Lead)
"""

import json

import pytest

from web.backend.result_mapper import (
    build_web_analysis_result,
)


def test_result_mapper_preserves_values():
    view = {
        "army_name": "Test Army",
        "total_points": 700,
        "metrics": (
            {"metric": "Offence", "value": 0.625},
        ),
        "scenarios": (
            {"scenario_id": "TEST", "score": 0.75},
        ),
        "provisional_capabilities": {
            "display_only": True,
            "metrics": (
                {
                    "label": "Magic",
                    "rating": None,
                    "status": "not_evaluated",
                },
            ),
        },
    }

    result = build_web_analysis_result(view)

    assert result["schema_version"] == (
        "palantir-web-analysis-v1"
    )
    assert result["analysis"]["total_points"] == 700
    assert result["analysis"]["metrics"][0]["value"] == 0.625
    assert result["analysis"]["scenarios"][0]["score"] == 0.75

    capability = result["analysis"][
        "provisional_capabilities"
    ]["metrics"][0]

    assert capability["rating"] is None
    assert capability["status"] == "not_evaluated"

    json.dumps(result, allow_nan=False)


def test_result_mapper_rejects_missing_data():
    with pytest.raises(ValueError, match="Missing analysis field"):
        build_web_analysis_result({"army_name": "Incomplete"})
