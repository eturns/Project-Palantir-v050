"""DEV-077-GUN-D2: read-only Gundabad data/import integrity inventory.

Not an army legality checker. Run from any directory:
    py -3.14 scripts/audit_gundabad_import_integrity.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
FIXTURE = ROOT / 'tests' / 'fixtures' / 'gundabadalloptions.json'
ROSTER = {
    'AZOG_THE_DEFILER', 'BOLG_SPAWN_OF_AZOG',
    'GUNDABAD_ORC_CAPTAIN', 'GOBLIN_MERCENARY_CAPTAIN',
    'GUNDABAD_CATAPULT_TROLL', 'TROLL_BRUTE',
    'GUNDABAD_ORC_WARRIOR', 'GUNDABAD_BERSERKER',
    'GOBLIN_MERCENARY', 'GUNDABAD_TROLL',
    'GUNDABAD_OGRE', 'WAR_BAT',
}

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))

def inventory(glob):
    paths = sorted(DATA.glob(glob))
    all_rows = []
    for path in paths:
        try:
            all_rows.extend((path, record) for record in rows(path))
        except (UnicodeError, csv.Error) as exc:
            print('  READ ERROR:', path.relative_to(ROOT), exc)
    return paths, all_rows

def sample(items, n=14):
    for item in items[:n]:
        print('   ', item)
    if len(items) > n:
        print(f'    ... {len(items)-n} additional entries')

def recursive_keys(value, prefix='$', depth=0):
    if depth > 6:
        return
    if isinstance(value, dict):
        for key, child in value.items():
            loc = f'{prefix}.{key}'
            yield loc, child
            yield from recursive_keys(child, loc, depth+1)
    elif isinstance(value, list):
        for i, child in enumerate(value[:100]):
            yield from recursive_keys(child, f'{prefix}[{i}]', depth+1)

def main():
    print('DEV-077-GUN-D2 — READ-ONLY IMPORT / CONFIGURATION AUDIT')
    print('Repository:', ROOT)
    print('Focus: fidelity of imported analysis inputs, NOT tournament legality')
    if not (ROOT / 'src' / 'army.py').exists():
        print('ERROR: Repository root mismatch; src/army.py not found.')
        return 2

    print('\n[PROFILE COVERAGE]')
    _, profiles = inventory('profiles/*profiles.csv')
    profile_index = {}
    for path, record in profiles:
        pid = record.get('id', '')
        if pid:
            profile_index.setdefault(pid, []).append((path, record))
    for pid in sorted(ROSTER):
        matches = profile_index.get(pid, [])
        if not matches:
            print('  MISSING:', pid)
        else:
            path, record = matches[0]
            print(f"  {pid}: {record.get('name')} | {record.get('points')} pts | {path.relative_to(ROOT)} | matches={len(matches)}")
    for pid in ('ORC_COMMANDER', 'WHITE_WARG_SEPARATED'):
        print('  linked component', pid, 'present=', pid in profile_index)

    print('\n[ARMY LIST LINKS]')
    membership = DATA / 'factions' / 'army_list_profiles.csv'
    if membership.exists():
        links = [r.get('profile_id') for r in rows(membership) if r.get('army_list_id') == 'GUNDABAD']
        print('  Gundabad member links:', len(links))
        print('  Missing book roster IDs:', sorted(ROSTER.difference(links)))
        print('  Linked profile IDs without profile record:', sorted({p for p in links if p not in profile_index}))
        print('  Extra linked IDs (includes valid composite components):', sorted(set(links)-ROSTER))
        duplicate = [p for p,c in Counter(links).items() if c>1]
        print('  Duplicate membership IDs:', duplicate)
    else:
        print('  MISSING:', membership.relative_to(ROOT))

    print('\n[OPTIONS DATA INVENTORY]')
    for filename in ('profile_options.csv','profile_option_wargear.csv','profile_option_mount.csv','profile_default_wargear.csv','profile_special_rules.csv','profile_heroic_actions.csv'):
        path = DATA / 'profiles' / filename
        if not path.exists():
            print('  MISSING:', path.relative_to(ROOT)); continue
        records = rows(path)
        fields = list(records[0]) if records else []
        relevant = [r for r in records if any(str(value) in ROSTER or str(value)=='ORC_COMMANDER' for key,value in r.items() if 'profile' in key.lower())]
        print(f'  {filename}: {len(records)} total rows; {len(relevant)} rows directly mentioning Gundabad roster/component')
        print('    columns:', ', '.join(fields))
        sample(relevant, 5)

    print('\n[IMPORTER MAPPING INVENTORY]')
    base = ROOT / 'src' / 'importers'
    if base.exists():
        hits = []
        for path in sorted(base.glob('*.py')):
            text = path.read_text(encoding='utf-8', errors='replace')
            matched = [token for token in ('GUNDABAD', 'TROLL_BRUTE', 'ORC_COMMANDER','GUNDABAD_CATAPULT_TROLL','BOLG_SPAWN_OF_AZOG') if token in text]
            if matched:
                hits.append((str(path.relative_to(ROOT)), ','.join(matched)))
        if hits: sample(hits, 30)
        else: print('  No exact canonical Gundabad tokens found: inspect external-ID mappings manually')
    else: print('  MISSING src/importers')

    print('\n[JSON FIXTURE]')
    if not FIXTURE.exists():
        print('  MISSING:', FIXTURE.relative_to(ROOT)); print('  Search for similarly named files:')
        sample([str(p.relative_to(ROOT)) for p in ROOT.rglob('*gundabad*json')][:30])
    else:
        try:
            data = json.loads(FIXTURE.read_text(encoding='utf-8-sig'))
            print('  Path:', FIXTURE.relative_to(ROOT))
            print('  Root type:', type(data).__name__)
            if isinstance(data, dict): print('  Root keys:', sorted(data))
            counts = Counter()
            for key, value in recursive_keys(data):
                if key.endswith(('.profileId','.profile_id','.id','.armyListId','.army_list_id','.points','.totalPoints')) and isinstance(value,(str,int,float)):
                    counts[(key.rsplit('.',1)[-1],str(value))]+=1
            print('  Selected identifiers and point values (not verified sums):')
            sample([(key, count) for key,count in counts.most_common(35)],35)
        except (OSError, ValueError) as exc: print('  FIXTURE READ ERROR:', exc)

    print('\n[CONCLUSIONS / REQUIRED RUNTIME CHECKS]')
    print('  1. Confirm importer resolves all Gundabad fixture IDs and selected options.')
    print('  2. Compare imported model counts and configured total points to export.')
    print('  3. Confirm composite Orc Commander/Troll Brute model accounting.')
    print('  4. Confirm no lost option equipment, mounts, or special rules.')
    print('  5. Keep JSON fixture valid for analysis even if not tournament legal.')
    print('  NOTE: static inventory does NOT prove importer runtime correctness.')
    print('No files modified.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
