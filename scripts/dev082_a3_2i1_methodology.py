"""DEV-082-A3-2I-1 six-army neutral-baseline methodology gate."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_six_army_validation import COHORT_FIXTURES
from offence_trapping_benchmark import build_trapping_qualified_offence_report
from offence_explicit_army_aggregation import make_fielded_offence_roster
from offence_aggregation_methodology import build_methodology_cohort


def load_army(path):
    result = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Real importer did not return an Army")
    return result["army"]


def main():
    fixtures = [(key, ROOT / "tests" / "fixtures" / name)
                for key, name in COHORT_FIXTURES]
    result = build_methodology_cohort(
        fixtures=fixtures,
        loader=load_army,
        reporter=build_trapping_qualified_offence_report,
        roster_builder=make_fielded_offence_roster,
    )
    # Small summary to keep PowerShell output usable; full individual model
    # probabilities are available through the pure report builder.
    summary = {
        k: v for k, v in result.items() if k != "rows"
    }
    summary["rows"] = [
        {k: v for k, v in row.items() if k != "profile_evidence"}
        for row in result["rows"]
    ]
    print(json.dumps(summary, indent=2, allow_nan=False))
    return result


if __name__ == "__main__":
    main()
