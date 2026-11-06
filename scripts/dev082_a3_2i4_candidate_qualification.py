"""Project Palantír DEV-082-A3-2I-4 — six-army read-only qualification.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
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
from offence_aggregation_methodology import METHOD
from offence_candidate_metric_qualification import audit_neutral_metric_cohort


def main():
    fixture_dir = ROOT / "tests" / "fixtures"
    fixtures = [(key, fixture_dir / name) for key, name in COHORT_FIXTURES]
    # Load once; all subsequent stages reuse each army's source evidence.
    source_rows = []
    for key, path in fixtures:
        army = load_army(path)
        source_rows.append((key, methodology_report(army, key),
                            weapon_report(army, key)))
    methodology = {
        "stage": "DEV-082-A3-2I-1", "status": "six_armies_qualified",
        "methodology": METHOD, "rows": [m for _, m, _ in source_rows],
        "candidate_raw_density": None, "calibration_changed": False,
        "production_scoring_changed": False,
    }
    # build_neutral_baseline_cohort expects loader + callbacks, which we
    # provide from the already loaded sources without another import.
    keyed = {key: (m, w) for key, m, w in source_rows}
    coverage = build_neutral_baseline_cohort(
        fixtures=[(key, key) for key, _ in fixtures],
        loader=lambda key: key,
        methodology_reporter=lambda _army, key: keyed[key][0],
        weapon_reporter=lambda _army, key: keyed[key][1],
    )
    numerical = compare_six_armies(coverage)
    qualified = audit_neutral_metric_cohort(numerical, coverage, methodology)
    concise = dict(qualified)
    concise["rows"] = [
        {k: v for k, v in row.items() if k != "entry_contributions"}
        for row in qualified["rows"]
    ]
    print(json.dumps(concise, indent=2, allow_nan=False))
    return qualified


if __name__ == "__main__":
    main()
