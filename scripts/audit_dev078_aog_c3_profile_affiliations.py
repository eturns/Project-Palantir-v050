"""DEV-078-AoG-C3 — guarded Hobbit profile-affiliation audit and migration.

Author: Edward Turns (Project Lead)

Default: read-only report. --apply adds factions column, but writes only
explicitly reviewed profile/faction assignments. Never derive it from a CSV
filename or from the race keyword. Existing nonempty values are preserved.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter
from pathlib import Path

FILES = (
    'dol_guldur', 'iron_hills', 'lake_town', 'gundabad', 'goblin_town',
    'three_trolls', 'smaug', 'erebor', 'dale', 'beornings', 'mirkwood'
)
# Explicit, small first-wave assignments. These are faction affiliations,
# NOT a declaration of race, army-list legality, or an inferred matchup score.
REVIEWED = {
    'BOFUR_CHAMPION_OF_EREBOR': ('EREBOR',),
    'IH_WR': ('IRON_HILLS',),
    'IH_DAIN': ('IRON_HILLS',),
    'IH_CAP': ('IRON_HILLS',),
    'IH_GR': ('IRON_HILLS',),
    'IH_CHARIOT': ('IRON_HILLS',),
    'IH_SIEGE_CREW': ('IRON_HILLS',),
}


def process(root: Path, apply: bool = False) -> list[tuple[str, str, str, str, str]]:
    report = []
    seen = set()
    for name in FILES:
        path = root / 'data' / 'profiles' / (name + '_profiles.csv')
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
            rows = list(reader)
        if not {'id', 'races', 'model_types'} <= set(fields):
            raise ValueError(f'{path}: missing classification fields')
        for row in rows:
            pid = row['id'].strip()
            if pid in seen:
                raise ValueError(f'Duplicate profile id across CSVs: {pid}')
            seen.add(pid)
            raw = (row.get('factions') or '').strip()
            existing = tuple(x.strip() for x in raw.split('|') if x.strip())
            suggested = REVIEWED.get(pid)
            if existing and suggested and set(existing) != set(suggested):
                raise ValueError(f'{pid}: existing affiliation {existing} conflicts with reviewed {suggested}')
            if existing:
                status = 'EXISTING'
                proposed = existing
            elif suggested:
                status = 'REVIEWED'
                proposed = suggested
            else:
                status = 'NEEDS_CANONICAL_REVIEW'
                proposed = ()
            report.append((name, pid, row['races'], '|'.join(proposed), status))
            if apply and suggested and not existing:
                row['factions'] = '|'.join(suggested)
        if apply:
            # Add field to every file consistently; unspecified values remain blank.
            if 'factions' not in fields:
                fields.append('factions')
            tmp = path.with_name(path.name + '.c3.tmp')
            with tmp.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
                writer.writeheader()
                writer.writerows(rows)
            tmp.replace(path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path, default=Path('dev078_aog_c3_affiliation_audit.csv'))
    args = parser.parse_args()
    report = process(args.root, args.apply)
    with args.report.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(('source_csv', 'profile_id', 'races', 'factions', 'status'))
        writer.writerows(report)
    counts = Counter(row[-1] for row in report)
    print(f'DEV-078-AoG-C3: {len(report)} unique profiles / {len(FILES)} CSVs')
    print(' '.join(f'{key}={value}' for key, value in sorted(counts.items())))
    print(f'Mode: {"APPLIED" if args.apply else "READ-ONLY"}; report: {args.report}')
    print('Only seven explicitly reviewed Erebor/Iron Hills identities are preassigned.')
    print('Unreviewed faction affiliations remain blank; no opponent score changes.')


if __name__ == '__main__':
    main()
