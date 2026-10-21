"""Idempotently register Mercenary Ambush while preserving local C2-C5 changes."""
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ensure(relative_path, row, identifying_fields):
    path = ROOT / relative_path
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    if not fields or not set(row).issubset(fields):
        raise ValueError(f'Unexpected CSV schema: {relative_path}')
    matches = [item for item in rows if all(
        (item.get(field) or '') == (row.get(field) or '') for field in identifying_fields
    )]
    if len(matches) > 1:
        raise ValueError(f'Duplicate CSV registration: {relative_path}: {row}')
    if matches:
        if any((matches[0].get(field) or '') != value for field, value in row.items()):
            raise ValueError(f'Conflicting CSV registration: {relative_path}: {row}')
        print(f'Already registered: {relative_path}: {row}')
        return
    shutil.copy2(path, path.with_suffix(path.suffix + '.c5b1.bak'))
    rows.append({field: row.get(field, '') for field in fields})
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(f'Registered: {relative_path}: {row}')


ensure('data/rules/special_rules.csv',
       {'id': 'MERCENARY_AMBUSH', 'name': 'Mercenary Ambush', 'category': 'SPECIAL'},
       ('id',))
for profile_id in ('GOBLIN_MERCENARY_CAPTAIN', 'GOBLIN_MERCENARY'):
    ensure('data/profiles/profile_special_rules.csv',
           {'profile_id': profile_id, 'rule_id': 'MERCENARY_AMBUSH', 'parameter': ''},
           ('profile_id', 'rule_id'))
