"""Project Palantír DEV-082-A3-2J-4C: align Offence with Magic layout.

Author: Edward Turns (Project Lead)

Presentation-only patch. Atomic preflight and backups; no scoring changes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

STAGE = 'DEV-082-A3-2J-4C'
IMPORT_OLD = "import { OffenceAnalysis, offenceHeadline, type ProvisionalOffence } from './OffenceAnalysis'"
IMPORT_NEW = "import { OffenceAnalysis, OffenceHeadlineBar, offenceHeadline, type ProvisionalOffence } from './OffenceAnalysis'"
TRACK_OLD = '                    {!isOffence && ('
TRACK_NEW = '''                    {isOffence && <OffenceHeadlineBar offence={army.provisional_offence} />}
                    {!isOffence && ('''


def patch_app(original: str) -> str:
    fully_patched = IMPORT_NEW in original and TRACK_NEW in original
    if fully_patched:
        return original
    if original.count(IMPORT_OLD) != 1 or original.count(TRACK_OLD) != 1:
        raise ValueError('Expected precisely one J-4B import and conditional track; no files changed')
    if '<OffenceAnalysis offence={army.provisional_offence} />' not in original:
        raise ValueError('J-4B inline Offence analysis is missing; no files changed')
    if IMPORT_NEW in original or TRACK_NEW in original:
        raise ValueError('Partial J-4C application detected; no files changed')
    return original.replace(IMPORT_OLD, IMPORT_NEW, 1).replace(TRACK_OLD, TRACK_NEW, 1)


def install(root: Path, package: Path) -> dict:
    frontend = root / 'web/frontend/src'
    app = frontend / 'App.tsx'
    source_files = [package / name for name in ('OffenceAnalysis.tsx', 'OffenceAnalysis.css')]
    if not app.is_file() or not all(p.is_file() for p in source_files):
        raise FileNotFoundError('Missing App.tsx or J-4C component source files')
    original = app.read_text(encoding='utf-8-sig')
    revised = patch_app(original)
    targets = [frontend / f.name for f in source_files]
    if not all(p.is_file() for p in targets):
        raise FileNotFoundError('J-4B component files missing; no files changed')
    for source, target in zip(source_files, targets):
        if 'DEV-082-A3-2J-4C' not in source.read_text(encoding='utf-8-sig'):
            raise ValueError(f'Unrecognised update source: {source}')
        if 'DEV-082-A3-2J-4B' not in target.read_text(encoding='utf-8-sig') and target.read_bytes() != source.read_bytes():
            raise ValueError(f'Expected installed J-4B component: {target}')
    if revised == original:
        if all(s.read_bytes() == t.read_bytes() for s,t in zip(source_files, targets)):
            return {'stage': STAGE, 'status': 'already_installed', 'scoring_modified': False}
        raise ValueError('App already modified, but component differs from J-4C package; no files changed')
    backups = [app.with_name('App.tsx.dev082_a3_2j4c.bak')]
    backups += [t.with_name(t.name + '.dev082_a3_2j4c.bak') for t in targets]
    if any(p.exists() for p in backups):
        raise FileExistsError('J-4C backup already exists; no files changed')
    # Validate all source and target files before writing any backup or edit.
    for file, backup in zip([app]+targets, backups):
        backup.write_bytes(file.read_bytes())
    for src, dst in zip(source_files, targets):
        dst.write_bytes(src.read_bytes())
    app.write_text(revised, encoding='utf-8')
    return {'stage': STAGE, 'status': 'installed', 'bar_added': True,
            'four_across_cards_added': True, 'production_scoring_changed': False,
            'calibration_changed': False, 'backend_modified': False,
            'backup': str(backups[0])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-dir', default='updates/dev082_a3_2j4c')
    args = parser.parse_args()
    print(json.dumps(install(Path.cwd(), Path(args.package_dir)), indent=2))


if __name__ == '__main__':
    main()
