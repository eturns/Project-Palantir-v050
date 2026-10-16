"""Compare current working tree scoring with committed HEAD (not DEV-073F).

Creates an isolated, detached temporary Git worktree, runs the repository's
validation script for four fixtures in both trees and compares 96 scenarios.
Never modifies historical snapshots, existing source or dashboard scores.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HISTORICAL = ROOT / 'docs' / 'validation' / 'dev073'
ARMIES = {
    'Five Armies': 'dev073f_five_armies_validation.json',
    'Garrison of Dale': 'dev073f_garrison_of_dale_validation.json',
    'Iron Hills': 'dev073f_iron_hills_validation.json',
    'Dol Guldur': 'dev073f_dol_guldur_700_validation.json',
}
TOL = 1e-10


def run(command: list[str], cwd: Path):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def calculate(repo: Path, fixture_name: str, output: Path) -> dict:
    runner = repo / 'run_dev073f_validation.py'
    fixture = repo / fixture_name
    if not runner.is_file() or not fixture.is_file():
        raise RuntimeError(f'Missing validation runner or fixture in {repo}')
    # Pass a RELATIVE fixture path: the legacy runner constructs ROOT / argv[1].
    # Windows may represent tempfile paths with 8.3 aliases, so passing an
    # absolute fixture path breaks FIXTURE.relative_to(ROOT) before JSON write.
    result = run([sys.executable, str(runner), fixture_name, str(output)], repo)
    post_write_print_error = (
        result.returncode != 0
        and output.is_file()
        and 'print(f"Baseline saved: {OUTPUT.relative_to(ROOT)}")' in result.stderr
        and 'ValueError:' in result.stderr
        and 'is not in the subpath of' in result.stderr
    )
    if result.returncode != 0 and not post_write_print_error:
        raise RuntimeError(f'Validation exited {result.returncode}:\n{(result.stdout + result.stderr)[-2000:]}')
    if not output.is_file():
        raise RuntimeError(f'Validation did not create {output}')
    return json.loads(output.read_text(encoding='utf-8'))


def same_number(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    return isinstance(a, (float, int)) and isinstance(b, (float, int)) and math.isfinite(a) and math.isfinite(b) and abs(a - b) <= TOL


def compare(name: str, before: dict, after: dict) -> list[str]:
    issues = []
    for field in ('benchmarks',):
        if before[field] != after[field]:
            issues.append(f'{name}: {field} changed')
    for field in ('points', 'points_limit', 'models'):
        if before['army'][field] != after['army'][field]:
            issues.append(f'{name}: army.{field} changed')
    old = {s['id']: s for s in before['scenarios']}
    new = {s['id']: s for s in after['scenarios']}
    if len(before['scenarios']) != 24 or len(after['scenarios']) != 24 or set(old) != set(new):
        issues.append(f'{name}: scenario list changed')
    for sid in sorted(old.keys() & new.keys()):
        a, b = old[sid], new[sid]
        if a['pool'] != b['pool']:
            issues.append(f'{name}/{sid}: pool changed')
        if not same_number(a['score'], b['score']):
            issues.append(f'{name}/{sid}: score {a["score"]:.12g} -> {b["score"]:.12g}')
        left = {d['dimension']: d for d in a['demands']}
        right = {d['dimension']: d for d in b['demands']}
        if left.keys() != right.keys():
            issues.append(f'{name}/{sid}: demand dimensions changed')
        for dim in left.keys() & right.keys():
            for field in ('capability', 'intensity'):
                if not same_number(left[dim][field], right[dim][field]):
                    issues.append(f'{name}/{sid}/{dim}/{field}: {left[dim][field]:.12g} -> {right[dim][field]:.12g}')
    return issues


def main() -> int:
    git = run(['git', 'rev-parse', '--show-toplevel'], ROOT)
    if git.returncode != 0 or Path(git.stdout.strip()).resolve() != ROOT.resolve():
        print('ERROR: Script must be saved and run from the Git repository root.', file=sys.stderr)
        return 2
    commit = run(['git', 'rev-parse', '--short', 'HEAD'], ROOT).stdout.strip()
    all_issues = []
    with tempfile.TemporaryDirectory(prefix='palantir_i2h_head_comparison_') as temp:
        temp_root = Path(temp)
        checkout = temp_root / 'committed_head'
        create = run(['git', 'worktree', 'add', '--detach', str(checkout), 'HEAD'], ROOT)
        if create.returncode != 0:
            print('ERROR: Could not create temporary Git worktree.\n' + create.stderr, file=sys.stderr)
            return 2
        try:
            for name, snapshot in ARMIES.items():
                try:
                    historical = json.loads((HISTORICAL / snapshot).read_text(encoding='utf-8'))
                    fixture_name = historical['fixture']
                    committed = calculate(checkout, fixture_name, temp_root / ('committed_' + snapshot))
                    current = calculate(ROOT, fixture_name, temp_root / ('current_' + snapshot))
                    issues = compare(name, committed, current)
                    if committed['fixture_sha256'] != current['fixture_sha256']:
                        # Git checkouts may apply different CRLF/LF conversions.
                        # Only disregard the byte-level difference when parsed
                        # fixture JSON is precisely identical between checkouts.
                        old_fixture = checkout / fixture_name
                        new_fixture = ROOT / fixture_name
                        old_data = json.loads(old_fixture.read_text(encoding='utf-8-sig'))
                        new_data = json.loads(new_fixture.read_text(encoding='utf-8-sig'))
                        if old_data != new_data:
                            issues.append(f'{name}: fixture content differs between HEAD and working tree')
                        else:
                            print(f'{name}: fixture bytes differ, but JSON input is identical (e.g. line endings)')
                    print(f'{name}: {len(current["scenarios"])} scenarios; {"PASS" if not issues else str(len(issues)) + " DIFFERENCES"}')
                    all_issues.extend(issues)
                except Exception as error:
                    all_issues.append(f'{name}: {error}')
        finally:
            remove = run(['git', 'worktree', 'remove', '--force', str(checkout)], ROOT)
            if remove.returncode != 0:
                print('WARNING: Temporary worktree cleanup failed.\n' + remove.stderr, file=sys.stderr)
    print(f'\nReference: committed HEAD {commit} | current uncommitted working tree | tolerance {TOL}')
    print('Historical validation snapshots and existing source files were not modified.')
    if all_issues:
        print(f'FAILED: {len(all_issues)} differences or errors')
        for entry in all_issues[:35]:
            print(' - ' + entry)
        if len(all_issues) > 35:
            print(f' ... plus {len(all_issues) - 35} more')
        return 1
    print('PASS: all 96 scores and all scenario demand values preserved relative to committed HEAD.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
