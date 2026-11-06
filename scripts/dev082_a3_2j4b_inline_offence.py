"""Project Palantír DEV-082-A3-2J-4B: inline Offence display.

Author: Edward Turns (Project Lead)

Only patches the J-4 React presentation. Does not change engine, scores,
scenario logic, calibration or API response. Refuses unfamiliar layouts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

OLD_IMPORT = "import { OffenceAnalysis, type ProvisionalOffence } from './OffenceAnalysis'"
NEW_IMPORT = "import { OffenceAnalysis, offenceHeadline, type ProvisionalOffence } from './OffenceAnalysis'"
OLD_STANDALONE = '          <OffenceAnalysis offence={army.provisional_offence} />\n\n'
OLD_NOTE = '''              The six qualified capability ratings use the frozen
              six-army reference, not the full range of MESBG armies.
              Magic's Casting Delivery range uses a separate provisional
              twelve-attempt reference. It is not an overall Magic score.
              Unavailable measurements are never treated as zero.
              Scenario scores are unchanged.'''
NEW_NOTE = '''              Existing calibrated capability ratings use the frozen six-army
              reference. Offence shows a neutral mechanical melee benchmark,
              not a calibrated overall rating. Magic's Casting Delivery
              uses a separate twelve-attempt reference, not an overall rating.
              Unavailable measurements are never treated as zero.
              Scenario scores are unchanged.'''


def replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise ValueError(f'{label}: expected exactly one anchor, found {count}; no files changed')
    return content.replace(old, new, 1)


def patch_app(original: str) -> str:
    if NEW_IMPORT in original and 'const isOffence = capability.metric_id' in original and OLD_STANDALONE not in original:
        return original
    out = original
    out = replace_once(out, OLD_IMPORT, NEW_IMPORT, 'component import')
    out = replace_once(out, OLD_STANDALONE, '', 'old standalone Offence panel')
    out = replace_once(
        out,
        "                const evaluated =\n                  capability.status === 'evaluated'",
        "                const isOffence = capability.metric_id === 'offence_density'\n"
        "                const evaluated =\n                  capability.status === 'evaluated'",
        'capability loop',
    )
    out = replace_once(
        out,
        '''                        {hasDelivery
                          ? `${lower!.toFixed(3)} – ${upper!.toFixed(3)} (provisional)`''',
        '''                        {isOffence
                          ? offenceHeadline(army.provisional_offence)
                          : hasDelivery
                            ? `${lower!.toFixed(3)} – ${upper!.toFixed(3)} (casting reference)`''',
        'capability header value',
    )
    out = replace_once(
        out,
        '''                      <strong>{capability.label}</strong>''',
        '''                      <strong>{isOffence ? 'Offence' : capability.label}</strong>''',
        'offence heading',
    )
    out = replace_once(
        out,
        '''                    <div
                      className="capability-track"''',
        '''                    {!isOffence && (
                    <div
                      className="capability-track"''',
        'legacy capability track',
    )
    out = replace_once(
        out,
        '''                    </div>

                    <div className="capability-detail">
                      {hasDelivery''',
        '''                    </div>
                    )}

                    <div className="capability-detail">
                      {isOffence
                        ? 'Neutral direct-melee reference · see breakdown below'
                        : hasDelivery''',
        'capability track close and summary',
    )
    out = replace_once(
        out,
        '''                    {magic && <ProvisionalMagicDetails magic={magic} />}''',
        '''                    {magic && <ProvisionalMagicDetails magic={magic} />}
                    {isOffence && <OffenceAnalysis offence={army.provisional_offence} />}''',
        'inline details after Magic',
    )
    out = replace_once(out, OLD_NOTE, NEW_NOTE, 'calibration disclosure')
    if out.count('<OffenceAnalysis offence={army.provisional_offence} />') != 1:
        raise ValueError('Offence component not present exactly once')
    if "const isOffence = capability.metric_id === 'offence_density'" not in out:
        raise ValueError('Offence metric binding missing')
    return out


def install(root: Path, source_dir: Path) -> dict:
    app = root / 'web/frontend/src/App.tsx'
    frontend = app.parent
    if not app.is_file():
        raise FileNotFoundError(f'Missing {app}')
    sources = [source_dir / 'OffenceAnalysis.tsx', source_dir / 'OffenceAnalysis.css']
    for src in sources:
        if not src.is_file():
            raise FileNotFoundError(f'Missing package component: {src}')
    original = app.read_text(encoding='utf-8-sig')
    revised = patch_app(original)
    if revised == original:
        # Still ensure components are the expected new version.
        for source in sources:
            target = frontend / source.name
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                raise ValueError(f'App already patched but {source.name} does not match package')
        return {'stage': 'DEV-082-A3-2J-4B', 'status': 'already_installed', 'scoring_modified': False}
    for source in sources:
        target = frontend / source.name
        if not target.is_file():
            raise FileNotFoundError(f'J-4 file missing: {target}')
        # J-4 must be installed before J-4B; preserve user modifications.
        if 'DEV-082-A3-2J-4' not in target.read_text(encoding='utf-8-sig'):
            raise ValueError(f'Unexpected J-4 file: {target}')
    backup = app.with_name('App.tsx.dev082_a3_2j4b.bak')
    if backup.exists():
        raise FileExistsError(f'Backup already exists: {backup}')
    for source in sources:
        dest = frontend / source.name
        prior = dest.with_name(dest.name + '.dev082_a3_2j4b.bak')
        if prior.exists():
            raise FileExistsError(f'Backup already exists: {prior}')
    # All validation above completes before first file write.
    backup.write_bytes(app.read_bytes())
    for source in sources:
        dest = frontend / source.name
        dest.with_name(dest.name + '.dev082_a3_2j4b.bak').write_bytes(dest.read_bytes())
    for source in sources:
        (frontend / source.name).write_bytes(source.read_bytes())
    app.write_text(revised, encoding='utf-8')
    return {'stage': 'DEV-082-A3-2J-4B', 'status': 'installed',
            'standalone_panel_removed': True, 'inline_offence_added': True,
            'scoring_modified': False, 'backend_modified': False,
            'backup': str(backup)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', default='web/frontend/src')
    args = parser.parse_args()
    print(json.dumps(install(Path.cwd(), Path(args.source_dir)), indent=2))

if __name__ == '__main__':
    main()
