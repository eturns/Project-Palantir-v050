"""Project Palantír DEV-082-A3-2J-4C layout and compatibility tests.
Author: Edward Turns (Project Lead)
"""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/dev082_a3_2j4c_magic_layout.py'
PACKAGE = ROOT / 'updates/dev082_a3_2j4c'
spec = importlib.util.spec_from_file_location('j4c', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MOCK_APP = '''import { OffenceAnalysis, offenceHeadline, type ProvisionalOffence } from './OffenceAnalysis'
function App() {
  const isOffence = capability.metric_id === 'offence_density'
  return <main>
                    <div className="capability-heading">Offence</div>
                    {!isOffence && (
                    <div className="capability-track"></div>
                    )}
                    {isOffence && <OffenceAnalysis offence={army.provisional_offence} />}
                    {magic && <ProvisionalMagicDetails magic={magic} />}
  </main>
}
'''


def test_inserts_neutral_bar_only_once():
    result = module.patch_app(MOCK_APP)
    assert result.count('<OffenceHeadlineBar offence={army.provisional_offence} />') == 1
    assert result.count('<OffenceAnalysis offence={army.provisional_offence} />') == 1
    assert result.count('{!isOffence && (') == 1
    assert 'ProvisionalMagicDetails' in result


def test_idempotent():
    x = module.patch_app(MOCK_APP)
    assert module.patch_app(x) == x


def test_fail_closed_partial():
    with pytest.raises(ValueError):
        module.patch_app(MOCK_APP.replace('offenceHeadline', 'otherHeadline'))


def test_unsupported_app_never_changes(tmp_path):
    folder = tmp_path / 'web/frontend/src'
    folder.mkdir(parents=True)
    (folder / 'App.tsx').write_text('custom', encoding='utf-8')
    for filename in ('OffenceAnalysis.tsx','OffenceAnalysis.css'):
        (folder / filename).write_text('DEV-082-A3-2J-4B', encoding='utf-8')
    with pytest.raises(ValueError):
        module.install(tmp_path, PACKAGE)
    assert not (folder / 'App.tsx.dev082_a3_2j4c.bak').exists()


def test_backup_and_idempotence(tmp_path):
    folder = tmp_path / 'web/frontend/src'
    folder.mkdir(parents=True)
    (folder / 'App.tsx').write_text(MOCK_APP, encoding='utf-8')
    for filename in ('OffenceAnalysis.tsx','OffenceAnalysis.css'):
        (folder / filename).write_text('DEV-082-A3-2J-4B previous component', encoding='utf-8')
    result = module.install(tmp_path, PACKAGE)
    assert result['status'] == 'installed'
    assert (folder / 'App.tsx.dev082_a3_2j4c.bak').read_text(encoding='utf-8') == MOCK_APP
    assert module.install(tmp_path, PACKAGE)['status'] == 'already_installed'


def test_four_cards_across_and_mobile():
    css = (PACKAGE / 'OffenceAnalysis.css').read_text(encoding='utf-8')
    assert 'repeat(4, minmax(0,1fr))' in css
    assert 'repeat(2, minmax(0,1fr))' in css
    assert 'grid-template-columns: 1fr' in css


def test_bar_not_misrepresented_as_calibration():
    content = (PACKAGE / 'OffenceAnalysis.tsx').read_text(encoding='utf-8')
    assert 'NEUTRAL_VISUAL_REFERENCE' in content
    assert 'not an overall Offence rating' in content
    assert 'role="img"' in content
    assert 'neutral.lower' in content and 'neutral.upper' in content
    assert 'neutral.value_type ===' in content
    assert 'Number.isFinite' in content
    assert '?? 0' not in content


def test_four_existing_cards_and_no_duplicate_figure():
    content = (PACKAGE / 'OffenceAnalysis.tsx').read_text(encoding='utf-8')
    for label in ('Charging', 'Supporting attacks', 'Trapping', 'Weapon alternatives'):
        assert f'<h3>{label}</h3>' in content
    assert '<div className="offence-figure">' not in content
    assert '<details className="offence-details"' in content
