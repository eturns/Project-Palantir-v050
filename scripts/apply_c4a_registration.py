"""Register Relentless Advance without replacing other local CSV updates."""
from pathlib import Path
import csv
import shutil

ROOT = Path(__file__).resolve().parents[1]

def register(relative_path, new_row, key_columns):
    path = ROOT / relative_path
    with path.open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or not set(new_row) <= set(fields):
        raise ValueError(f'Unexpected CSV header in {path}')
    key = tuple(new_row[c] for c in key_columns)
    matches = [r for r in rows if tuple(r[c] for c in key_columns) == key]
    if matches:
        if len(matches) > 1 or any(any((r.get(c) or '') != (new_row.get(c) or '') for c in new_row) for r in matches):
            raise ValueError(f'Conflicting registration: {key}')
        print(f'Already registered: {key}')
        return
    shutil.copy2(path, path.with_suffix(path.suffix + '.c4a.bak'))
    rows.append({c: new_row.get(c, '') for c in fields})
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(f'Registered: {key}')

register('data/rules/special_rules.csv',
         {'id': 'RELENTLESS_ADVANCE', 'name': 'Relentless Advance', 'category': 'MOVEMENT'},
         ('id',))
register('data/profiles/profile_special_rules.csv',
         {'profile_id': 'GUNDABAD_OGRE', 'rule_id': 'RELENTLESS_ADVANCE', 'parameter': ''},
         ('profile_id', 'rule_id'))
