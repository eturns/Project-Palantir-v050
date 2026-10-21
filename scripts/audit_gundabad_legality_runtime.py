"""DEV-077-GUN-D1-B: read-only local legality wiring and data audit.

Run from any directory: py -3.14 scripts/audit_gundabad_legality_runtime.py
No Project Palantir modules are imported and no project files are written.
"""
from __future__ import annotations

import ast
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
DATA = ROOT / 'data'

WATCH_FUNCTIONS = {
    'validate', 'validate_army', 'analyse_imported_army',
    'analyse_mesbg_list_builder_file', 'import_army_from_mesbg_list_builder',
    'warband_composition_rule_allows', 'warband_composition_rule_applies_to_member',
    'build_legal_multi_group_candidates', 'filter_legal_candidates',
}
WATCH_TERMS = (
    'warband_composition_rule', 'profile_quantity_relation_rule',
    'max_in_army', 'points_limit', 'independent', 'heroic_status',
    'warband_capacity', 'validate_army', '.validate(',
)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def parse_source(path: Path):
    try:
        return ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    except (SyntaxError, UnicodeError) as exc:
        print('  PARSE ERROR', relative(path), str(exc))
        return None


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return dotted(node.value) + '.' + node.attr
    return ''


def csv_rows(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def inventory_csv():
    print('\n[ARMY / COMPOSITION DATA]')
    for path in sorted(DATA.rglob('*.csv')):
        name = path.name.casefold()
        if not any(term in name for term in ('warband', 'composition', 'quantity_relation', 'army_list', 'profile_classification')):
            continue
        try:
            rows = csv_rows(path)
        except (OSError, csv.Error) as exc:
            print('  CSV ERROR', relative(path), exc)
            continue
        matches = [row for row in rows if 'GUNDABAD' in ' '.join(str(v) for v in row.values()).upper()]
        print(f'  {relative(path)} rows={len(rows)} gundabad_mentions={len(matches)}')
        for row in matches[:12]:
            print('   ', row)
        if len(matches) > 12:
            print(f'    ... {len(matches)-12} more Gundabad-mention rows')


def inventory_python():
    print('\n[VALIDATION DECLARATIONS AND CALL SITES — static evidence only]')
    declarations = []
    calls = []
    for path in sorted(SRC.rglob('*.py')):
        if '__pycache__' in path.parts:
            continue
        tree = parse_source(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                node.name in WATCH_FUNCTIONS or any(x in node.name.casefold() for x in ('warband', 'legality', 'composition'))
            ):
                declarations.append((relative(path), node.lineno, node.name))
            if isinstance(node, ast.Call):
                name = dotted(node.func)
                if name and (name.split('.')[-1] in WATCH_FUNCTIONS or any(x in name.casefold() for x in ('warband_composition_rule', 'profile_quantity_relation_rule'))):
                    calls.append((relative(path), node.lineno, name))
    print('  Key functions:')
    for path, line, name in declarations:
        print(f'    {path}:{line}  def {name}')
    print('  Call sites:')
    for path, line, name in calls:
        print(f'    {path}:{line}  {name}(...)')
    print(f'  Total declarations={len(declarations)} call_sites={len(calls)}')
    print('  NOTE: Static call sites do not prove execution or correct rejection.')


def key_source_lines():
    print('\n[KEY FILE EVIDENCE — matching lines, capped per file]')
    paths = [
        'army.py', 'army_list.py', 'validation/army.py',
        'services/army_analysis_service.py', 'services/mesbg_list_analysis_service.py',
        'services/mesbg_list_builder_import_service.py',
        'warband_composition_rule.py', 'warband_composition_rule_matcher.py',
        'profile_quantity_relation_rule.py', 'profile_quantity_relation_rule_matcher.py',
        'importers/mesbg_list_builder_importer.py',
    ]
    for sub in paths:
        path = SRC / sub
        if not path.is_file():
            print(f'  {sub}: NOT PRESENT')
            continue
        lines = path.read_text(encoding='utf-8-sig').splitlines()
        found = [(i, line.strip()) for i, line in enumerate(lines, 1) if any(term in line.casefold() for term in WATCH_TERMS)]
        print(f'  {relative(path)}: {len(found)} matching lines')
        for line_no, line in found[:22]:
            print(f'    L{line_no}: {line[:150]}')
        if len(found) > 22:
            print(f'    ... {len(found)-22} further matching lines')


def main():
    print('DEV-077-GUN-D1-B — READ-ONLY LEGALITY WIRING AUDIT')
    print('Repository:', ROOT)
    if not (SRC / 'army.py').is_file() or not DATA.is_dir():
        raise SystemExit('ERROR: repository path incorrect; src/army.py and data/ required. No audit conclusions.')
    inventory_csv()
    inventory_python()
    key_source_lines()
    print('\n[CONCLUSION] This is an inventory, not a legality verdict.')
    print('NO claims of valid/invalid warbands, independent-hero capacity, or composite costs without runtime test fixtures.')
    print('No files modified.')


if __name__ == '__main__':
    main()
