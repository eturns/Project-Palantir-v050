"""DEV-082-A3-2B — real-army shadow Offence report, no production changes."""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from main import run_analysis_workflow
from offence_real_army_comparison import build_real_army_offence_comparison


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        raise SystemExit(
            "Usage: python scripts/dev082_a3_2b_compare_offence.py "
            "tests/fixtures/dol_guldur_700.json"
        )
    fixture = Path(args[0])
    if not fixture.is_file():
        raise SystemExit(f"Fixture not found: {fixture}")
    result = run_analysis_workflow(str(fixture), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise SystemExit("Production importer did not return a real Army")
    report = build_real_army_offence_comparison(result["army"])
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
