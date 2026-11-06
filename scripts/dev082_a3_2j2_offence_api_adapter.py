"""Project Palantír — DEV-082-A3-2J-2 opt-in JSON API contract diagnostic.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Reuses the previous six-army qualified presentation runner, but does NOT
modify FastAPI, invoke a live endpoint, or alter analysis/scenario scores.
"""
from pathlib import Path
import json
import sys
import io
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from dev082_a3_2j1_presentation_contract import main as presentation_preview
from web.backend.offence_diagnostic_adapter import build_provisional_offence_api_evidence
from web.backend.result_mapper import build_web_analysis_result


def main():
    # The J-1 runner prints the entire diagnostic record; keep this wave concise.
    with redirect_stdout(io.StringIO()):
        cohort = presentation_preview()
    if cohort.get("status") != "six_armies_presentation_contract_qualified":
        raise ValueError("Six-army presentation cohort was not qualified")
    rows = cohort["preview_rows"]
    if len(rows) != 6:
        raise ValueError("Expected exactly six reference armies")
    api_rows = []
    for row in rows:
        # Demonstrate optional mapper output with a synthetic minimal view.
        view = {
            "army_name": row["army_key"], "total_points": 700,
            "metrics": {"offence": "unchanged-placeholder"},
            "scenarios": [], "provisional_capabilities": {"metrics": []},
        }
        before = build_web_analysis_result(view)
        view["provisional_offence"] = row
        after = build_web_analysis_result(view)
        remaining = dict(after["analysis"])
        provisional = remaining.pop("provisional_offence")
        if remaining != before["analysis"]:
            raise ValueError("Historical API analysis changed")
        if provisional != build_provisional_offence_api_evidence(row):
            raise ValueError("Offence mapper mismatch")
        api_rows.append({
            "army_key": provisional["army_key"],
            "status": provisional["status"],
            "neutral_melee": provisional["neutral_melee"],
            "support_equipped_models": provisional["conditional_capabilities"]["support"]["equipped_models"],
            "production_scoring_changed": False,
        })
    output = {
        "stage": "DEV-082-A3-2J-2",
        "status": "six_armies_opt_in_api_contract_qualified",
        "armies": len(api_rows), "models": cohort["models"],
        "historical_api_fields_preserved": True,
        "normal_uploads_without_diagnostic_unchanged": True,
        "diagnostic_populated_by_live_analysis": False,
        "endpoint_modified": False,
        "frontend_modified": False,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "scenario_score": None,
        "dashboard_score": None,
        "rows": api_rows,
    }
    print(json.dumps(output, indent=2, allow_nan=False))
    return output


if __name__ == "__main__":
    main()
