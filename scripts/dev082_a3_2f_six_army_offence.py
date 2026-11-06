"""DEV-082-A3-2F: read-only six-army Offence validation runner."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from main import run_analysis_workflow
from offence_trapping_benchmark import build_trapping_qualified_offence_report
from offence_six_army_validation import build_six_army_offence_cohort


def load_army(path):
    result = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Production importer did not return an Army")
    return result["army"]


def main():
    fixture_dir = ROOT / "tests" / "fixtures"
    report = build_six_army_offence_cohort(
        fixture_dir=fixture_dir,
        loader=load_army,
        reporter=build_trapping_qualified_offence_report,
    )
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
