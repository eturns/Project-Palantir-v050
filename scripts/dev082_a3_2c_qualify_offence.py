"""DEV-082-A3-2C: qualify real-army shadow Offence evidence, read-only."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from main import run_analysis_workflow
from offence_evidence_qualification import build_qualified_offence_report


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        raise SystemExit('Usage: python scripts/dev082_a3_2c_qualify_offence.py tests/fixtures/dol_guldur_700.json')
    path = Path(args[0])
    if not path.is_file():
        raise SystemExit(f'Fixture not found: {path}')
    workflow = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(workflow, dict) or workflow.get('army') is None:
        raise SystemExit('Production import did not return an Army')
    report = build_qualified_offence_report(workflow['army'])
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == '__main__':
    main()
