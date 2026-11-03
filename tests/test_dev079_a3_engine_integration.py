"""DEV-079-A3-3 — real engine integration acceptance.

Author: Edward Turns (Project Lead)
"""

import json
from pathlib import Path

from desktop_analysis_adapter import run_analysis
from web.backend.engine_adapter import analyse_army_for_web
from web.backend.result_mapper import build_web_analysis_result


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dol_guldur_700.json"
)


def test_web_matches_existing_engine():
    original = run_analysis(str(FIXTURE))
    assert original is not None

    web_result = analyse_army_for_web(FIXTURE)

    # Exact parity, including scenario scores and
    # all provisional capability evidence.
    expected = build_web_analysis_result(original)

    assert web_result == expected

    analysis = web_result["analysis"]

    assert analysis["army_name"] == "Eddie's choice"
    assert analysis["total_points"] == 700
    assert analysis["model_count"] == 11
    assert len(analysis["metrics"]) == 10
    assert len(analysis["scenarios"]) == 24
    assert len(
        analysis["provisional_capabilities"]["metrics"]
    ) == 11

    # Ensure the complete response is valid JSON.
    json.dumps(web_result, allow_nan=False)
