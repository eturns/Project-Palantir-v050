"""Register Troll Brute Trample without replacing current local CSV contents."""
import csv
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data" / "profiles" / "gundabad_profiles.csv"
RULES = ROOT / 'data/rules/special_rules.csv'
ASSIGNMENTS = ROOT / 'data/profiles/profile_special_rules.csv'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader.fieldnames or []), list(reader)


def ensure_row(path, values, keys):
    fields, rows = read_csv(path)
    if not fields or not all(k in fields for k in values):
        raise ValueError(f'Unexpected CSV schema: {path}')
    matches = [row for row in rows if all(row[key] == values[key] for key in keys)]
    if matches:
        if len(matches) > 1:
            raise ValueError(f'Duplicate existing registration: {values}')
        return False
    backup = path.with_suffix(path.suffix + '.c6a.bak')
    if not backup.exists():
        shutil.copy2(path, backup)
    rows.append({k: values.get(k, '') for k in fields})
    with path.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    return True


def main():
    # This package needs the actual model profile ID, not the kit/composition ID.
    # Abort rather than silently registering a non-existent unit.
    _, profiles = read_csv(PROFILES)
    existing = {row['id'] for row in profiles}
    candidates = existing & {'TROLL_BRUTE', 'GUNDABAD_TROLL_BRUTE'}
    if len(candidates) != 1:
        raise ValueError(
            f'Could not uniquely identify Troll Brute profile: {sorted(candidates)}; '
            'verify its canonical profile ID before registration.'
        )
    profile_id = next(iter(candidates))
    if profile_id != 'TROLL_BRUTE':
        raise ValueError(
            f'Found {profile_id}; first update TROLL_BRUTE_PROFILE_ID in '
            'src/gundabad_troll_brute_trample.py to match your repository.'
        )
    print('Rule added:', ensure_row(RULES, {
        'id': 'TRAMPLE', 'name': 'Trample', 'category': 'MOVEMENT',
    }, ('id',)))
    print('Assignment added:', ensure_row(ASSIGNMENTS, {
        'profile_id': profile_id, 'rule_id': 'TRAMPLE', 'parameter': '',
    }, ('profile_id', 'rule_id')))


if __name__ == '__main__':
    main()
