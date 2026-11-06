"""DEV-082-A3-2D — real-army weapon qualification runner, read-only."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from main import run_analysis_workflow
from offence_weapon_qualification import build_weapon_qualified_offence_report


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        raise SystemExit('Usage: python scripts/dev082_a3_2d_weapons.py tests/fixtures/dol_guldur_700.json')
    fixture = Path(args[0])
    if not fixture.is_file():
        raise SystemExit(f'Fixture not found: {fixture}')
    result = run_analysis_workflow(str(fixture), print_report=False)
    if not isinstance(result, dict) or result.get('army') is None:
        raise SystemExit('Production workflow did not return an Army')
    report = build_weapon_qualified_offence_report(result['army'])
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == '__main__':
    main()
