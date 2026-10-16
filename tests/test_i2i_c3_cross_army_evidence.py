"""Focused contract tests for the mixed-points repository fixture runner."""
from pathlib import Path
from unittest.mock import Mock
import pytest

from i2i_c3_cross_army_evidence import REFERENCE_CASES, plan, execute, validate_case


def document(points):
    return {"points": points, "models": 8, "production_scoring_enabled": False,
            "reference_anchors_approved": False, "scenario_scoring_changed": False,
            "measurements": [{} for _ in range(10)], "analysis_commit": "a" * 40,
            "roster_sha256": "b" * 64, "available_count": 5,
            "partial_count": 1, "unresolved_metrics": ["magic"]}


def test_exact_three_historical_fixtures():
    assert [(key, pts) for key, _, pts, _ in REFERENCE_CASES] == [
        ("iron_hills", 823), ("garrison_of_dale", 177), ("five_armies", 346)]


def test_all_three_explicitly_good():
    assert all(alignment == "Good" for *_, alignment in REFERENCE_CASES)


def test_plan_does_not_invent_700_points(tmp_path):
    rows = plan(tmp_path)
    assert [r[3] for r in rows] == [823, 177, 346]
    assert rows[0][2] == tmp_path / "iron_hills_evidence.json"


def test_valid_document():
    assert validate_case("example", document(823), 823)


@pytest.mark.parametrize("field", ["production_scoring_enabled", "reference_anchors_approved", "scenario_scoring_changed"])
def test_rejects_scoring_or_approval(field):
    d = document(823)
    d[field] = True
    with pytest.raises(ValueError):
        validate_case("example", d, 823)


def test_rejects_wrong_point_total():
    with pytest.raises(ValueError, match="Unexpected points"):
        validate_case("example", document(700), 823)


def test_rejects_incomplete_metric_inventory():
    d = document(823)
    d["measurements"] = []
    with pytest.raises(ValueError, match="ten"):
        validate_case("example", d, 823)


def test_missing_input_prevents_any_run(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    runner = Mock()
    with pytest.raises(FileNotFoundError):
        execute(tmp_path, runner=runner)
    runner.assert_not_called()


def test_existing_output_prevents_any_run(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    monkeypatch.setattr(Path, "exists", lambda self: True)
    runner = Mock()
    with pytest.raises(FileExistsError):
        execute(tmp_path, runner=runner)
    runner.assert_not_called()


def test_runner_collects_three_without_modifying_engine(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    monkeypatch.setattr(Path, "exists", lambda self: False)
    lookup = {key: points for key, _, points, _ in REFERENCE_CASES}
    calls = []
    def fake_run(fixture, output, key):
        calls.append((fixture, output, key))
        return document(lookup[key])
    rows = execute(tmp_path, runner=fake_run)
    assert len(rows) == len(calls) == 3
    assert [r["points"] for r in rows] == [823, 177, 346]
