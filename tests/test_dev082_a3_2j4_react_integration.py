"""Project Palantír — DEV-082-A3-2J-4 frontend integration static guards.

Author: Edward Turns (Project Lead). No backend or scoring engine modified.
"""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'dev082_a3_2j4_install_react.py'
spec = spec_from_file_location('offence_react_installer', SCRIPT)
module = module_from_spec(spec)
spec.loader.exec_module(module)

MOCK_APP = '''import { useState } from 'react'
import './App.css'

type ArmyAnalysis = {
  provisional_magic?: ProvisionalMagic
  strengths: Assessment[]
}

function App() {
  return <main>
          <section className="panel">
            <h2>Strengths &amp; Weaknesses</h2>
            <p>Unchanged legacy content</p>
          </section>
        </main>
}
'''


def test_patcher_only_adds_three_required_bindings():
    out = module.patch_app(MOCK_APP)
    assert out.count('OffenceAnalysis') == 3  # import, JSX tag, prop type
    assert 'Unchanged legacy content' in out
    assert 'provisional_magic?: ProvisionalMagic' in out


def test_patcher_is_idempotent():
    out = module.patch_app(MOCK_APP)
    assert module.patch_app(out) == out


def test_partial_patch_fails_closed():
    with pytest.raises(ValueError, match='Partially'):
        module.patch_app(MOCK_APP.replace("import './App.css'", "import './App.css'\n" + module.IMPORT_LINE))


def test_missing_anchor_fails_closed():
    with pytest.raises(ValueError):
        module.patch_app(MOCK_APP.replace('Strengths &amp; Weaknesses', 'Other'))


def test_installer_writes_backup_and_remains_idempotent(tmp_path):
    frontend = tmp_path / 'web' / 'frontend' / 'src'
    frontend.mkdir(parents=True)
    (frontend / 'App.tsx').write_text(MOCK_APP)
    src = ROOT / 'web' / 'frontend' / 'src'
    first = module.install(tmp_path, src)
    assert first['status'] == 'installed'
    assert (frontend / 'App.tsx.dev082_a3_2j4.bak').read_text() == MOCK_APP
    assert 'OffenceAnalysis' in (frontend / 'App.tsx').read_text()
    second = module.install(tmp_path, src)
    assert second['status'] == 'already_installed'
    assert second['app_modified'] is False


def test_component_has_explicit_unqualified_case():
    content = (ROOT / 'web/frontend/src/OffenceAnalysis.tsx').read_text()
    assert "offence?.status === 'not_qualified'" in content
    assert 'unavailable does not mean zero' in content
    # J-4B deliberately keeps the inline expander in the capability row.
    # Missing evidence must show an explicit unavailable state, never zero.
    assert "if (!offence || !isQualified(offence) || !offence.neutral_melee) return 'Not evaluated'" in content
    assert 'No qualified mechanical melee evidence is available for this upload.' in content
    assert '<div className="offence-unavailable" role="status">' in content


def test_component_never_renders_numeric_zero_for_null_evidence():
    content = (ROOT / 'web/frontend/src/OffenceAnalysis.tsx').read_text()
    assert 'neutral.value_type' in content
    assert "offence!.neutral_melee!" in content
    assert '?? 0' not in content


def test_preserves_scenarios_magic_and_legacy_graph():
    output = module.patch_app(MOCK_APP)
    assert output.count('provisional_magic?: ProvisionalMagic') == 1
    assert output.count('<h2>Strengths &amp; Weaknesses</h2>') == 1
    assert 'provisional_offence?: ProvisionalOffence | null' in output


def test_mobile_layout_and_accessible_details():
    css = (ROOT / 'web/frontend/src/OffenceAnalysis.css').read_text()
    component = (ROOT / 'web/frontend/src/OffenceAnalysis.tsx').read_text()
    assert '@media (max-width: 650px)' in css
    assert 'grid-template-columns: 1fr' in css
    # Native details/summary provides the expander's accessible name.
    # The former standalone panel used aria-labelledby, but J-4B is inline.
    assert '<details className="offence-details"' in component
    assert '<summary>View Offence analysis</summary>' in component


def test_no_new_chart_calibration_or_fetch():
    component = (ROOT / 'web/frontend/src/OffenceAnalysis.tsx').read_text()
    assert 'fetch(' not in component
    assert 'useEffect' not in component
    assert 'setArmy(' not in component
    assert 'rankedScenarios' not in component


def test_rejects_mismatched_existing_component(tmp_path):
    frontend = tmp_path / 'web' / 'frontend' / 'src'
    frontend.mkdir(parents=True)
    (frontend / 'App.tsx').write_text(MOCK_APP)
    (frontend / 'OffenceAnalysis.tsx').write_text('different custom content')
    with pytest.raises(FileExistsError):
        module.install(tmp_path, ROOT / 'web/frontend/src')
