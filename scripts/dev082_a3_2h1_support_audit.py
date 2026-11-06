"""Project Palantír — DEV-082-A3-2H-1 support architecture audit."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_six_army_validation import COHORT_FIXTURES
from offence_support_architecture_audit import build_six_army_support_audit


def load_army(path):
    result = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Production workflow did not return an Army")
    return result["army"]


def main():
    fixtures = [(key, ROOT / "tests" / "fixtures" / filename)
                for key, filename in COHORT_FIXTURES]
    report = build_six_army_support_audit(
        fixtures=fixtures,
        loader=load_army,
        src_dir=ROOT / "src",
    )
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
