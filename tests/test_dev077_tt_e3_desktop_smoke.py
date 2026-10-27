"""DEV-077-TT-E3: actual workflow -> desktop adapter smoke test.

The test invokes full runtime data loading for 400/700/1000-point roster JSONs.
No Tk window is opened; on-screen visual confirmation is separate.
"""
from __future__ import annotations
import json
from pathlib import Path

import pytest

from main import run_analysis_workflow
from desktop_analysis_adapter import run_analysis
from desktop_app import build_army_summary, build_capability_analysis_summary
from three_trolls_upgrades import THREE_TROLLS_UPGRADE_NAMES

FIXTURE = Path(__file__).parent / "fixtures" / "the_three_trolls_all_options.json"
PROFILES = {"TT_BILL", "TT_BERT", "TT_TOM"}


def _write_roster(tmp_path, count):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["metadata"]["tttSpecialUpgrades"] = list(THREE_TROLLS_UPGRADE_NAMES[:count])
    data["metadata"]["maxPoints"] = 400 + count * 50
    path = tmp_path / f"three_trolls_{400+count*50}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


@pytest.mark.parametrize("count,expected", [(0,400),(6,700),(12,1000)])
def test_actual_workflow_imports_correct_points_and_diagnostics(tmp_path, count, expected):
    path = _write_roster(tmp_path, count)
    result = run_analysis_workflow(str(path), print_report=False)
    assert result is not None, "Workflow returned no analysis"
    definition, army = result["definition"], result["army"]
    assert definition.army_list_id == "THREE_TROLLS"
    assert army.total_points() == expected
    assert army.purchase_points == count * 50
    assert {m.profile_id for m in army.fielded_models()} == PROFILES
    assert len(army.fielded_models()) == 3
    assert not result["analysis"]["validation_errors"]
    diagnostic = result["analysis"].get("mechanical_three_trolls_upgrades")
    assert diagnostic is not None, "The upgrade diagnostic was lost in the analysis service"
    assert len(diagnostic.available_effect_keys) == count
    assert diagnostic.hoard.purchase_points == 50 * count
    assert "metric_assessments" in result["analysis"]
    assert "battlefield_assessments" in result["analysis"]


@pytest.mark.parametrize("count,expected", [(0,400),(6,700),(12,1000)])
def test_real_desktop_adapter_renders_army_and_capabilities(tmp_path, count, expected):
    path = _write_roster(tmp_path, count)
    view = run_analysis(str(path))
    assert view is not None, "Desktop adapter returned no view"
    assert view["total_points"] == expected
    assert view["points_limit"] == expected
    assert view["model_count"] == 3
    assert view["is_legal"] is True
    assert len(view["key_models"]) == 3
    assert sum(m["points"] for m in view["key_models"]) == 400
    summary = build_army_summary(view)
    assert f"{expected} / {expected} pts" in summary
    assert "Models: 3" in summary
    capability = build_capability_analysis_summary(view)
    assert isinstance(capability, str) and capability.strip()
    assert view.get("provisional_capabilities") is not None
    assert view["provisional_capabilities"]["display_only"] is True
    assert view["provisional_capabilities"]["production_scoring_changed"] is False


def test_desktop_evidence_visibility_is_explicitly_a_separate_gap():
    """Document current presentation contract; do not claim upgrade UI exists."""
    from desktop_analysis_view_model import build_desktop_analysis_view_model
    # The view-model builder currently has no upgrade-diagnostic presentation key.
    # This is a monitored known gap, not a failing assertion on future improvement.
    import inspect
    source = inspect.getsource(build_desktop_analysis_view_model)
    if "mechanical_three_trolls_upgrades" not in source:
        pytest.skip("Known UI gap: upgrade diagnostics are not rendered in desktop view")
