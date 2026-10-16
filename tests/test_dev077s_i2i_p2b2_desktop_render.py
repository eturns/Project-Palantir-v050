"""Focused B2 tests for the existing Tkinter rendering hook."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from install_p2b2_desktop import updated_source, install


SAMPLE = '''def build_capability_analysis_summary(view_model: dict) -> str:\n    return "LEGACY"\n\ndef unchanged():\n    return 42\n'''


def _function(source):
    namespace = {}
    exec(compile(source, '<updated>', 'exec'), namespace)
    return namespace['build_capability_analysis_summary'], namespace


def test_updater_preserves_existing_functions():
    source = updated_source(SAMPLE)
    fn, ns = _function(source)
    assert fn({}) == 'LEGACY'
    assert ns['unchanged']() == 42
    assert updated_source(source) == source
    assert len([n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'build_capability_analysis_summary']) == 1


def test_provisional_panel_uses_formatter(monkeypatch):
    module = SimpleNamespace(build_provisional_summary=lambda data: 'PROVISIONAL BAR')
    monkeypatch.setitem(sys.modules, 'provisional_desktop_view', module)
    fn, _ = _function(updated_source(SAMPLE))
    panel = {'display_only': True, 'production_scoring_changed': False,
             'defence_independent_composite_weighting_allowed': False}
    assert fn({'provisional_capabilities': panel}) == 'PROVISIONAL BAR'


@pytest.mark.parametrize('bad_key,bad_value', [
    ('display_only', False),
    ('production_scoring_changed', True),
    ('defence_independent_composite_weighting_allowed', True),
])
def test_provisional_contract_is_enforced(bad_key, bad_value):
    fn, _ = _function(updated_source(SAMPLE))
    panel = {'display_only': True, 'production_scoring_changed': False,
             'defence_independent_composite_weighting_allowed': False}
    panel[bad_key] = bad_value
    with pytest.raises(ValueError):
        fn({'provisional_capabilities': panel})


def test_installer_creates_backup_and_is_idempotent(tmp_path):
    path = tmp_path / 'desktop_app.py'
    path.write_text(SAMPLE, encoding='utf-8')
    assert install(path) is True
    assert path.with_suffix('.py.p2b2.bak').read_text(encoding='utf-8') == SAMPLE
    assert install(path) is False


def test_installer_refuses_to_overwrite_existing_backup(tmp_path):
    path = tmp_path / 'desktop_app.py'
    path.write_text(SAMPLE, encoding='utf-8')
    path.with_suffix('.py.p2b2.bak').write_text('existing', encoding='utf-8')
    with pytest.raises(FileExistsError):
        install(path)
    assert path.read_text(encoding='utf-8') == SAMPLE
