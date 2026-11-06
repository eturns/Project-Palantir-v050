"""Project Palantír — DEV-082-A3-2J-1 six-army presentation preview.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
Does not connect to or change the live FastAPI/React website.
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
from offence_presentation_contract import build_offence_presentation_cohort
from army_offence_capability import calculate_army_offensive_output_density


def main():
    armies = []
    sources = []
    for key, name in COHORT_FIXTURES:
        imported = run_analysis_workflow(
            str(ROOT / "tests" / "fixtures" / name), print_report=False)
        if not isinstance(imported, dict) or imported.get("army") is None:
            raise ValueError(f"Import failed for {key}")
        army = imported["army"]
        armies.append(army)
        sources.append((key, methodology_report(army, key), weapon_report(army, key)))
    methodology = {
        "stage": "DEV-082-A3-2I-1", "status": "six_armies_qualified",
        "rows": [m for _, m, _ in sources],
        "candidate_raw_density": None, "calibration_changed": False,
        "production_scoring_changed": False,
    }
    keyed = {key: (m, w) for key, m, w in sources}
    coverage = build_neutral_baseline_cohort(
        fixtures=[(key, key) for key, _, _ in sources],
        loader=lambda key: key,
        methodology_reporter=lambda _unused, key: keyed[key][0],
        weapon_reporter=lambda _unused, key: keyed[key][1],
    )
    numerical = compare_six_armies(coverage)
    qualified = audit_neutral_metric_cohort(numerical, coverage, methodology)
    attribution = attribute_six_armies(
        qualified, armies,
        production_calculator=lambda army: calculate_army_offensive_output_density(
            army, charge_probability=1.0),
    )
    output = build_offence_presentation_cohort(attribution, qualified, coverage)
    print(json.dumps(output, indent=2, allow_nan=False))
    return output


if __name__ == "__main__":
    main()
