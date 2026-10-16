"""D7-B tests check actual submitted export layouts and evidence safeguards."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import i2i_c3_real_army_validation as mod


@pytest.fixture
def export_file(tmp_path):
    p = tmp_path / "roster.json"
    p.write_text(json.dumps({
        "armyList": "Rangers of Mirkwood", "edition": "v2024",
        "warbands": [
            {"meta": {"points": 250, "bows": 0}, "units": [{"quantity": 10}]},
            {"meta": {"points": 235, "bows": 0}, "units": [{"quantity": 10}]},
            {"meta": {"points": 215, "bows": 0}, "units": [{"quantity": 10}]},
        ],
    }), encoding="utf-8")
    return p


def example_document(*, points=700, models=33, shooting=0.2):
    return {
        "points": points, "models": models,
        "measurements": [
            {"metric": "shooting", "availability": "available",
             "value": shooting},
        ],
    }


def test_export_points(export_file):
    assert mod.inspect_export(export_file)["export_points"] == 700


def test_export_models(export_file):
    assert mod.inspect_export(export_file)["export_models"] == 33


def test_zero_bow_limit_is_not_absence_of_bows(export_file):
    assert mod.inspect_export(export_file)["export_bow_limit_count"] == 0
    assert mod.review_evidence(example_document(),
        army_key="rangers_of_mirkwood_700",
        export=mod.inspect_export(export_file)) == ()


def test_rangers_zero_shooting_is_blocked(export_file):
    assert "rangers_default_bow_shooting_not_resolved" in mod.review_evidence(
        example_document(shooting=0), army_key="rangers_of_mirkwood_700",
        export=mod.inspect_export(export_file))


def test_rangers_missing_shooting_is_blocked(export_file):
    assert mod.review_evidence(example_document(shooting=None),
        army_key="rangers_of_mirkwood_700",
        export=mod.inspect_export(export_file))


def test_azogs_zero_shooting_not_special_cased(export_file):
    assert mod.review_evidence(example_document(shooting=0),
        army_key="azogs_hunters_700",
        export=mod.inspect_export(export_file)) == ()


@pytest.mark.parametrize("points", [694, 701])
def test_points_out_of_bounds_blocked(export_file, points):
    assert "engine_points_outside_695_700" in mod.review_evidence(
        example_document(points=points), army_key="azogs_hunters_700",
        export=mod.inspect_export(export_file))


@pytest.mark.parametrize("points", [695, 700])
def test_points_boundaries_pass_when_export_matches(export_file, points):
    export=mod.inspect_export(export_file)
    export["export_points"]=points
    assert not mod.review_evidence(
        example_document(points=points), army_key="azogs_hunters_700",
        export=export)


def test_export_mismatch_blocked(export_file):
    assert "engine_export_points_mismatch" in mod.review_evidence(
        example_document(points=697), army_key="azogs_hunters_700",
        export=mod.inspect_export(export_file))


def test_model_mismatch_blocked(export_file):
    assert "engine_export_model_count_mismatch" in mod.review_evidence(
        example_document(models=32), army_key="azogs_hunters_700",
        export=mod.inspect_export(export_file))


def test_missing_fixture_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        mod.validate_roster(fixture=tmp_path/"missing.json", output=tmp_path/"out.json",
                            army_key="a", alignment="Good", archetype="shooting")


def test_no_overwrite(export_file, tmp_path):
    output=tmp_path/"existing.json"
    output.write_text("existing")
    with pytest.raises(ValueError, match="overwrite"):
        mod.validate_roster(fixture=export_file, output=output,
                            army_key="a", alignment="Good", archetype="shooting")


def test_failed_shooting_does_not_save(export_file, tmp_path):
    output=tmp_path/"out.json"
    def fake_intake(**kwargs):
        Path(kwargs["output"]).write_text(json.dumps(example_document(shooting=0)))
        return {"blockers": [], "points_and_evidence_qualified": True}
    with patch.object(mod, "intake_roster", side_effect=fake_intake):
        result = mod.validate_roster(
            fixture=export_file, output=output,
            army_key="rangers_of_mirkwood_700",
            alignment="Good", archetype="shooting")
    assert result["blockers"] == ["rangers_default_bow_shooting_not_resolved"]
    assert not output.exists()


def test_success_is_still_not_anchor_approval(export_file, tmp_path):
    output=tmp_path/"out.json"
    def fake_intake(**kwargs):
        Path(kwargs["output"]).write_text(json.dumps(example_document()))
        return {"blockers": [], "points_and_evidence_qualified": True}
    with patch.object(mod, "intake_roster", side_effect=fake_intake):
        result=mod.validate_roster(
            fixture=export_file, output=output,
            army_key="rangers_of_mirkwood_700",
            alignment="Good", archetype="shooting")
    assert output.exists()
    assert result["calibration_eligible"] is False
    assert result["anchors_approved"] is False


def test_roster_names():
    assert set(mod.ROSTERS) == {"azogs_hunters_700", "rangers_of_mirkwood_700"}
