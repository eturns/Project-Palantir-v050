"""Project Palantír DEV-082-A3-2J-4B frontend contract checks.
Author: Edward Turns (Project Lead).
"""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'web/frontend/src'
spec = importlib.util.spec_from_file_location('inline_installer', ROOT / 'scripts/dev082_a3_2j4b_inline_offence.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MOCK_APP = '''import { useState } from 'react'
import './App.css'
import { OffenceAnalysis, type ProvisionalOffence } from './OffenceAnalysis'
type ArmyAnalysis = { provisional_offence?: ProvisionalOffence | null }
function App() {
  const army = {provisional_offence: null}
  return <main>
            <div className="capability-list">
              {army.provisional_capabilities.metrics.map((capability) => {
                const evaluated =
                  capability.status === 'evaluated' &&
                  capability.rating !== null
                const magic = capability.metric_id === 'magic'
                const hasDelivery = false
                const lower = 0
                const upper = 0
                const score = 0
                return (
                  <div className="capability" key={capability.metric_id}>
                    <div className="capability-heading">
                      <strong>{capability.label}</strong>
                      <span>
                        {hasDelivery
                          ? `${lower!.toFixed(3)} – ${upper!.toFixed(3)} (provisional)`
                          : score !== null ? score.toFixed(3) : 'Not evaluated'}
                      </span>
                    </div>
                    <div
                      className="capability-track"
                      role="progressbar"
                    >
                      {score}
                    </div>

                    <div className="capability-detail">
                      {hasDelivery
                        ? 'Casting'
                        : 'Raw'}
                    </div>
                    {magic && <ProvisionalMagicDetails magic={magic} />}
                  </div>
                )
              })}
            </div>
            <p className="capability-note">
              The six qualified capability ratings use the frozen
              six-army reference, not the full range of MESBG armies.
              Magic's Casting Delivery range uses a separate provisional
              twelve-attempt reference. It is not an overall Magic score.
              Unavailable measurements are never treated as zero.
              Scenario scores are unchanged.
            </p>
          <OffenceAnalysis offence={army.provisional_offence} />

          <section className="panel"><h2>Strengths &amp; Weaknesses</h2></section>
       </main>
}
'''


def test_patching_adds_inline_reuse_and_removes_standalone():
    result = module.patch_app(MOCK_APP)
    assert result.count('<OffenceAnalysis offence={army.provisional_offence} />') == 1
    assert '{isOffence && <OffenceAnalysis offence={army.provisional_offence} />}' in result
    assert "const isOffence = capability.metric_id === 'offence_density'" in result
    assert "isOffence ? 'Offence' : capability.label" in result
    assert "offenceHeadline(army.provisional_offence)" in result
    assert '{!isOffence && (' in result
    assert 'Existing calibrated capability ratings' in result
    assert "<h2>Strengths &amp; Weaknesses</h2>" in result


def test_patcher_idempotent():
    transformed = module.patch_app(MOCK_APP)
    assert module.patch_app(transformed) == transformed


def test_unexpected_layout_fails_closed():
    with pytest.raises(ValueError):
        module.patch_app(MOCK_APP.replace('OffenceAnalysis offence', 'Other offence'))


def test_non_offence_magic_detail_kept():
    result = module.patch_app(MOCK_APP)
    assert result.count('{magic && <ProvisionalMagicDetails magic={magic} />}') == 1


def test_no_standalone_panel_component():
    component = (SRC / 'OffenceAnalysis.tsx').read_text()
    assert '<section className="panel offence-panel"' not in component
    assert '<details className="offence-details"' in component
    assert 'export function offenceHeadline' in component


def test_unqualified_is_not_zero():
    component = (SRC / 'OffenceAnalysis.tsx').read_text()
    assert "return 'Not evaluated'" in component
    assert 'unavailable does not mean zero' in component
    assert '?? 0' not in component


def test_conditional_values_not_promoted():
    component = (SRC / 'OffenceAnalysis.tsx').read_text()
    assert 'is_overall_army_offence === false' in component
    assert 'n.value_type' in component
    assert 'not an overall Offence rating' in component
    assert 'not added automatically' in component


def test_mobile_and_pluralisation():
    css = (SRC / 'OffenceAnalysis.css').read_text()
    component = (SRC / 'OffenceAnalysis.tsx').read_text()
    assert 'grid-template-columns: 1fr' in css
    assert "? 'model carries' : 'models carry'" in component


def test_installer_backup_and_idempotency(tmp_path):
    folder = tmp_path / 'web/frontend/src'
    folder.mkdir(parents=True)
    (folder / 'App.tsx').write_text(MOCK_APP, encoding='utf-8')
    # Build local J-4-like files in the temporary project. Never reference
    # the developer's /mnt/data workspace: it does not exist on Windows.
    for filename in ('OffenceAnalysis.tsx', 'OffenceAnalysis.css'):
        marker = ('// ' if filename.endswith('.tsx') else '/* ')
        suffix = '' if filename.endswith('.tsx') else ' */'
        prior_content = (
            f'{marker}DEV-082-A3-2J-4 previous component{suffix}\n'
            + (SRC / filename).read_text(encoding='utf-8-sig')
        )
        (folder / filename).write_text(prior_content, encoding='utf-8')
    result = module.install(tmp_path, SRC)
    assert result['status'] == 'installed'
    assert (folder / 'App.tsx.dev082_a3_2j4b.bak').read_text(encoding='utf-8') == MOCK_APP
    assert module.install(tmp_path, SRC)['status'] == 'already_installed'


def test_installer_unknown_file_no_writes(tmp_path):
    folder = tmp_path / 'web/frontend/src'
    folder.mkdir(parents=True)
    (folder / 'App.tsx').write_text(MOCK_APP, encoding='utf-8')
    for filename in ('OffenceAnalysis.tsx', 'OffenceAnalysis.css'):
        (folder / filename).write_text('user-customized')
    with pytest.raises(ValueError):
        module.install(tmp_path, SRC)
    assert not (folder / 'App.tsx.dev082_a3_2j4b.bak').exists()
