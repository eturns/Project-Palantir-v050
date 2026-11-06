"""Project Palantír — DEV-082-A3-2J-4 minimal React integration.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
Run from repository root. Non-destructive installer, idempotent and backed up.
"""
from __future__ import annotations

import shutil
from pathlib import Path

IMPORT_LINE = "import { OffenceAnalysis, type ProvisionalOffence } from './OffenceAnalysis'\n"
TYPE_MARKER = '  provisional_magic?: ProvisionalMagic\n'
TYPE_ADDITION = '  provisional_offence?: ProvisionalOffence | null\n'
LOCATION_MARKER = '''          <section className="panel">
            <h2>Strengths &amp; Weaknesses</h2>'''
COMPONENT_INSERT = '''          <OffenceAnalysis offence={army.provisional_offence} />

'''


def patch_app(source: str) -> str:
    """Only touch three exact anchors; refuse ambiguous/outdated layouts."""
    if all(x in source for x in (IMPORT_LINE.strip(), TYPE_ADDITION.strip(),
                                 COMPONENT_INSERT.strip())):
        return source
    if any(x in source for x in (IMPORT_LINE.strip(), TYPE_ADDITION.strip(),
                                 COMPONENT_INSERT.strip())):
        raise ValueError("Partially installed J-4 integration; inspect App.tsx manually")
    if source.count("import './App.css'") != 1:
        raise ValueError("Could not uniquely identify App.css import")
    if source.count(TYPE_MARKER) != 1:
        raise ValueError("Could not uniquely identify ArmyAnalysis type")
    if source.count(LOCATION_MARKER) != 1:
        raise ValueError("Could not uniquely identify Strengths & Weaknesses section")
    return (source
            .replace("import './App.css'\n", "import './App.css'\n" + IMPORT_LINE, 1)
            .replace(TYPE_MARKER, TYPE_MARKER + TYPE_ADDITION, 1)
            .replace(LOCATION_MARKER, COMPONENT_INSERT + LOCATION_MARKER, 1))


def install(root: Path, component_source: Path) -> dict:
    root = root.resolve()
    frontend = root / 'web' / 'frontend' / 'src'
    app = frontend / 'App.tsx'
    if not app.is_file():
        raise FileNotFoundError(f"Cannot find React App.tsx at {app}")
    component_source = component_source.resolve()
    for filename in ('OffenceAnalysis.tsx', 'OffenceAnalysis.css'):
        src = component_source / filename
        if not src.is_file():
            raise FileNotFoundError(f"Missing download: {src}")
    original = app.read_text(encoding='utf-8-sig')
    revised = patch_app(original)
    changed = revised != original
    if changed:
        backup = app.with_suffix('.tsx.dev082_a3_2j4.bak')
        if backup.exists():
            raise FileExistsError(f"Refusing to overwrite previous App.tsx backup: {backup}")
        shutil.copy2(app, backup)
    for filename in ('OffenceAnalysis.tsx', 'OffenceAnalysis.css'):
        dest = frontend / filename
        source = component_source / filename
        if dest.exists() and dest.read_bytes() != source.read_bytes():
            raise FileExistsError(f"Refusing to overwrite existing modified component: {dest}")
        if source != dest:
            shutil.copy2(source, dest)
    if changed:
        app.write_text(revised, encoding='utf-8')
    return {"stage": "DEV-082-A3-2J-4", "status": "installed" if changed else "already_installed",
            "app_modified": changed,
            "files": [str(frontend / 'OffenceAnalysis.tsx'),
                      str(frontend / 'OffenceAnalysis.css')],
            "scoring_modified": False, "backend_modified": False}


def main() -> None:
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', required=True,
                        help='Folder containing both downloaded OffenceAnalysis files')
    args = parser.parse_args()
    print(json.dumps(install(Path.cwd(), Path(args.source_dir)), indent=2))


if __name__ == '__main__':
    main()
