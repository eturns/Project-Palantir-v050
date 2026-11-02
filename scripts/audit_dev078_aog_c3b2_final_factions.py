"""Project Palantir — DEV-078-AoG-C3-B2: final 15 faction confirmations.
Author: Edward Turns (Project Lead)

Run from repository root. Read-only by default; --apply updates ONLY the 15
explicitly confirmed model rows. Does not edit races, army membership or rules.
"""
from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path

# User-confirmed canonical profile factions. Preserve spelling verbatim.
CONFIRMED = {
    'DG_HOC': 'GUNDABAD',
    'DG_HOW': 'GUNDABAD',
    'DG_HOWR': 'GUNDABAD',
    'DG_FW': 'GUNDABAD',
    'YAZNEG': 'GUNDABAD',
    'NARZUG': 'GUNDABAD',
    'FIMBUL': 'GUNDABAD',
    'THRAIN_THE_BROKEN': 'EREBOR',
    'GT_GOLLUM': 'GOBLIN-TOWN',
    'SMAUG': 'EREBOR',
    'TT_BILL': 'TROLLSHAWS',
    'TT_BERT': 'TROLLSHAWS',
    'TT_TOM': 'TROLLSHAWS',
    'BEORN': 'BEORNING',
    'BEORN_THE_BEAR': 'BEORNING',
}
FILES = (
    'dol_guldur_profiles.csv', 'gundabad_profiles.csv',
    'goblin_town_profiles.csv', 'three_trolls_profiles.csv',
    'smaug_profiles.csv', 'beornings_profiles.csv',
)


def process(root: Path, *, apply: bool = False) -> dict[str, int]:
    """Prevalidate all files and exact profile IDs before any mutation.

    Existing different faction values are conflicts and are never overwritten.
    Returns summary counts; unrecognised additional profile records are untouched.
    """
    root = Path(root)
    replacements: list[tuple[Path, str]] = []
    matched: dict[str, str] = {}
    pending = 0
    already = 0
    for filename in FILES:
        path = root / 'data' / 'profiles' / filename
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            if fields is None or not {'id', 'races', 'factions'}.issubset(fields):
                raise ValueError(f'Missing required columns in {path}')
            rows = list(reader)
        if any(None in row for row in rows):
            raise ValueError(f'Malformed CSV row: {path}')
        changed = False
        for row in rows:
            pid = row['id']
            if pid not in CONFIRMED:
                continue
            if pid in matched:
                raise ValueError(f'Duplicate confirmed profile ID: {pid}')
            expected = CONFIRMED[pid]
            current = (row['factions'] or '').strip()
            if current and current != expected:
                raise ValueError(
                    f'Faction conflict: {pid}: CSV has {current!r}; '
                    f'confirmed {expected!r}. No files updated.'
                )
            matched[pid] = expected
            if current == expected:
                already += 1
            else:
                row['factions'] = expected
                changed = True
                pending += 1
        if changed:
            output = io.StringIO(newline='')
            writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            replacements.append((path, output.getvalue()))
    missing = set(CONFIRMED) - set(matched)
    if missing:
        raise ValueError(f'Unresolved confirmed IDs: {sorted(missing)}. No files updated.')
    if apply:
        for path, content in replacements:
            path.write_text(content, encoding='utf-8', newline='')
    summary = {'confirmed': len(CONFIRMED), 'already_matching': already,
               'pending_assignments': pending, 'files_to_update': len(replacements)}
    print(f"Confirmed: {summary['confirmed']} | matching: {already} | "
          f"to assign: {pending} | files: {len(replacements)} | "
          f"mode: {'APPLY' if apply else 'READ-ONLY'}")
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    process(Path.cwd(), apply=args.apply)
