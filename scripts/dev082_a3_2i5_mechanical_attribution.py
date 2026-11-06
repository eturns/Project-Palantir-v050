"""Project Palantír DEV-082-A3-2I-5 six-army mechanical attribution.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
No changes to production scores, calibration or dashboard.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from main import run_analysis_workflow
from offence_six_army_validation import COHORT_FIXTURES
from dev082_a3_2i2_neutral_completeness import methodology_report, weapon_report
from offence_neutral_baseline_completeness import build_neutral_baseline_cohort
from offence_neutral_mechanical_comparison import compare_six_armies
from offence_candidate_metric_qualification import audit_neutral_metric_cohort
from offence_mechanical_attribution import attribute_six_armies
from army_offence_capability import calculate_army_offensive_output_density


def main():
    armies = []
    sources = []
    for key, name in COHORT_FIXTURES:
        path = ROOT / "tests" / "fixtures" / name
        result = run_analysis_workflow(str(path), print_report=False)
        if not isinstance(result, dict) or result.get("army") is None:
            raise ValueError(f"Real army workflow failed for {key}")
        army = result["army"]
        armies.append(army)
        sources.append((key, methodology_report(army, key), weapon_report(army, key)))
    methodology = {
        "stage": "DEV-082-A3-2I-1", "status": "six_armies_qualified",
        "rows": [m for _, m, _ in sources],
        "candidate_raw_density": None, "calibration_changed": False,
        "production_scoring_changed": False,
    }
    keys = {key: (m, w) for key, m, w in sources}
    coverage = build_neutral_baseline_cohort(
        fixtures=[(key, key) for key, _, _ in sources],
        loader=lambda key: key,
        methodology_reporter=lambda _unused, key: keys[key][0],
        weapon_reporter=lambda _unused, key: keys[key][1],
    )
    if coverage["status"] != "six_armies_qualified":
        raise ValueError("A3-2I-2 coverage validation incomplete")
    numerical = compare_six_armies(coverage)
    qualified = audit_neutral_metric_cohort(numerical, coverage, methodology)
    result = attribute_six_armies(
        qualified, armies,
        production_calculator=lambda army: calculate_army_offensive_output_density(
            army, charge_probability=1.0),
    )
    concise = dict(result)
    concise["rows"] = [
        {k: v for k, v in row.items() if k != "profile_rows_evidence"}
        for row in result["rows"]
    ]
    print(json.dumps(concise, indent=2, allow_nan=False))
    return result


if __name__ == "__main__":
    main()
