"""DEV-082-A3-2E: standalone, read-only trapping comparison runner."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from main import run_analysis_workflow
from offence_trapping_benchmark import build_trapping_qualified_offence_report


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit('Usage: python scripts/dev082_a3_2e_trapping.py tests/fixtures/dol_guldur_700.json')
    fixture = Path(args[0])
    if not fixture.is_file():
        raise SystemExit(f'Fixture not found: {fixture}')
    workflow = run_analysis_workflow(str(fixture), print_report=False)
    if not isinstance(workflow, dict) or workflow.get('army') is None:
        raise SystemExit('Production workflow did not return an Army')
    report = build_trapping_qualified_offence_report(workflow['army'])
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == '__main__':
    main()
