"""DEV-077-GUN-D1: read-only Gundabad data and legality inventory.

Produces observations, not verdicts about all rules being satisfied.
No source/data files are modified.
"""
import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name == 'scripts' else Path.cwd()
PROFILES = ROOT / 'data/profiles'
EXPECTED = {
    'Azog the Defiler', 'Bolg, Spawn of Azog', 'Gundabad Orc Captain',
    'Goblin Mercenary Captain', 'Troll Brute', 'Gundabad Catapult Troll',
    'Gundabad Orc Warrior', 'Gundabad Berserker', 'Goblin Mercenary',
    'Gundabad Troll', 'Gundabad Ogre', 'War Bat',
}

def rows(path):
    if not path.exists():
        return []
    with path.open(encoding='utf-8-sig', newline='') as fp:
        return list(csv.DictReader(fp))

def scan_functions(path):
    if not path.exists():
        return []
    try:
        root = ast.parse(path.read_text(encoding='utf-8-sig'))
    except (UnicodeError, SyntaxError) as exc:
        return [f'PARSE ERROR: {exc}']
    return sorted({node.name for node in ast.walk(root)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and ('valid' in node.name.lower() or 'warband' in node.name.lower()
                        or 'composition' in node.name.lower())})

def main():
    print('DEV-077-GUN-D1 — READ-ONLY COMPOSITION AUDIT')
    print('Repository:', ROOT)
    profile_files = sorted(PROFILES.glob('*profiles.csv'))
    all_rows = [(p.name, row) for p in profile_files for row in rows(p)]
    matches = [(p, row) for p, row in all_rows if row.get('name', '').strip() in EXPECTED]
    print('\n[2024 BOOK ROSTER — matched by exact display name]')
    found = set()
    for p, row in sorted(matches, key=lambda x: x[1].get('name', '')):
        found.add(row['name'].strip())
        print(f"  {row['name']}: id={row.get('id')} points={row.get('points')} "
              f"heroic_status={row.get('heroic_status')} file={p}")
    print('  Expected roster names matched:', len(found), 'of', len(EXPECTED))
    print('  Unmatched (check aliases/composite models manually):', sorted(EXPECTED - found))
    print('\n[ARMY LIST REGISTRATION]')
    for path in sorted((ROOT/'data').rglob('*.csv')):
        if path.name == 'army_lists.csv':
            for row in rows(path):
                if 'gundabad' in ' '.join(row.values()).lower():
                    print(' ',path.relative_to(ROOT),row)
    print('\n[COMPOSITION / RELATIONSHIP CSV INVENTORY]')
    for path in sorted((ROOT/'data').rglob('*.csv')):
        if any(k in path.name for k in ('warband','quantity_relation','composition','army_list_profile')):
            rr=rows(path)
            selected=[r for r in rr if 'gundabad' in str(r).lower() or 'troll_brute' in str(r).lower() or 'mercenary' in str(r).lower()]
            print(' ',path.relative_to(ROOT),'total_rows=',len(rr),'relevant_rows=',len(selected))
            for row in selected[:12]: print('   ',row)
            if len(selected)>12: print('    ... additional rows omitted')
    print('\n[VALIDATOR FUNCTION INVENTORY — presence is not runtime proof]')
    names=('src/army.py','src/validation/army.py','src/warband_composition_rule.py',
           'src/warband_composition_rule_matcher.py','src/composition_resolver.py',
           'src/services/mesbg_list_analysis_service.py')
    for name in names:
        path=ROOT/name
        print(' ',name,'present=',path.exists(),'functions=',scan_functions(path))
    print('\n[IMPORTANT] Match does not establish warband legality, hero quotas, ' 
          'Troll Brute combined cost, Independent Hero limits or model-specific exceptions.')
    print('No files modified.')

if __name__ == '__main__':
    main()
