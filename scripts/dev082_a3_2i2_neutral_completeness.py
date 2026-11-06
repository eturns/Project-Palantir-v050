"""Project Palantír — DEV-082-A3-2I-2 six-army neutral coverage audit.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
Read-only. No candidate score, automatic weapon selection or scenario change.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_six_army_validation import COHORT_FIXTURES
from offence_trapping_benchmark import build_trapping_qualified_offence_report
from offence_weapon_qualification import build_weapon_qualified_offence_report
from offence_explicit_army_aggregation import make_fielded_offence_roster
from offence_aggregation_methodology import classify_army_methodology
from offence_multi_weapon_audit import audit_multi_weapon_report
from offence_weapon_resolution_policy import qualify_multi_weapon_cohort
from offence_neutral_baseline_completeness import build_neutral_baseline_cohort


def load_army(path):
    result = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Real workflow did not return Army")
    return result["army"]


def methodology_report(army, key):
    return classify_army_methodology(
        key,
        build_trapping_qualified_offence_report(army),
        make_fielded_offence_roster(army),
    )


def weapon_report(army, key):
    audit = audit_multi_weapon_report(
        build_weapon_qualified_offence_report(army), key=key,
    )
    cohort = {
        "stage": "DEV-082-A3-2G-1", "status": "complete",
        "armies_expected": 1, "rows": [audit],
        "multi_weapon_models": audit["multiple_weapon_models"],
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
    }
    qualified = qualify_multi_weapon_cohort(cohort)
    if qualified["status"] != "complete" or qualified["armies_qualified"] != 1:
        raise ValueError("Weapon policy not fully qualified")
    return qualified["rows"][0]


def main():
    fixture_dir = ROOT / "tests" / "fixtures"
    report = build_neutral_baseline_cohort(
        fixtures=[(key, fixture_dir / name) for key, name in COHORT_FIXTURES],
        loader=load_army,
        methodology_reporter=methodology_report,
        weapon_reporter=weapon_report,
    )
    summary = {key: value for key, value in report.items() if key != "rows"}
    summary["rows"] = [
        {key: value for key, value in row.items() if key != "profile_evidence"}
        for row in report["rows"]
    ]
    print(json.dumps(summary, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
