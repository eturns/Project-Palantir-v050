"""DEV-082-A3-2G-2 — audit the six reference armies without scoring."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_six_army_validation import COHORT_FIXTURES
from offence_weapon_qualification import build_weapon_qualified_offence_report
from offence_multi_weapon_audit import build_multi_weapon_cohort
from offence_weapon_resolution_policy import qualify_multi_weapon_cohort


def load_army(path):
    result = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Unable to import actual army")
    return result["army"]


def main():
    fixtures = [(key, ROOT / "tests" / "fixtures" / name)
                for key, name in COHORT_FIXTURES]
    first_stage = build_multi_weapon_cohort(
        fixtures=fixtures,
        loader=load_army,
        weapon_reporter=build_weapon_qualified_offence_report,
    )
    result = qualify_multi_weapon_cohort(first_stage)
    print(json.dumps(result, indent=2, allow_nan=False))
    return result


if __name__ == "__main__":
    main()
