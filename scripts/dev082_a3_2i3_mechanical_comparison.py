"""Project Palantír — DEV-082-A3-2I-3 six-army numeric comparison.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
Diagnostic only. Does not modify frozen calibration, site or existing metric.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from offence_six_army_validation import COHORT_FIXTURES
from dev082_a3_2i2_neutral_completeness import (
    load_army, methodology_report, weapon_report,
)
from offence_neutral_baseline_completeness import build_neutral_baseline_cohort
from offence_neutral_mechanical_comparison import compare_six_armies


def main():
    fixtures = [(key, ROOT / "tests" / "fixtures" / name)
                for key, name in COHORT_FIXTURES]
    coverage = build_neutral_baseline_cohort(
        fixtures=fixtures,
        loader=load_army,
        methodology_reporter=methodology_report,
        weapon_reporter=weapon_report,
    )
    if coverage["status"] != "six_armies_qualified":
        print(json.dumps({"stage": "DEV-082-A3-2I-3", "status": "blocked",
                          "coverage": coverage}, indent=2, allow_nan=False))
        raise RuntimeError("Incomplete six-army neutral reference coverage")
    result = compare_six_armies(coverage)
    concise = dict(result)
    concise["rows"] = [{key: value for key, value in row.items()
                       if key != "per_entry_evidence"} for row in result["rows"]]
    print(json.dumps(concise, indent=2, allow_nan=False))
    return result


if __name__ == "__main__":
    main()
