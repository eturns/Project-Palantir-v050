import json
from pathlib import Path
import pytest
from i2i_c3_b8a_cohort_intake import inspect_fixture, audit_one, audit_cohort, FIXTURES


def write_fixture(tmp_path, points=700, count=3):
    payload = {
        "metadata":{"maxPoints":700},
        "edition":"v2024","armyList":"Test",
        "warbands":[{"hero":{"model_id":"hero","options":[]},
                     "units":[{"model_id":"warrior","quantity":count-1,"options":[]}],
                     "meta":{"points":points}}]}
    path=tmp_path/"list.json"
    path.write_text(json.dumps(payload),encoding="utf-8")
    return path


def test_point_and_model_intake(tmp_path):
    report=inspect_fixture(write_fixture(tmp_path))
    assert report["declared_points"]==700
    assert report["models"]==3
    assert report["warbands"]==1


def test_below_point_limit_blocked(tmp_path):
    write_fixture(tmp_path,points=694)
    row=audit_one("x","list.json","Good","test",tmp_path,
                  importer=lambda path: (_ for _ in ()).throw(RuntimeError("ignored")))
    assert "points_outside_695_700" in row["issues"]


def test_missing_fixture_reported(tmp_path):
    row=audit_one("x","not_there.json","Good","test",tmp_path)
    assert row["status"]=="blocked"
    assert "fixture_missing" in row["issues"]


def test_successful_import_with_matching_totals(tmp_path):
    write_fixture(tmp_path)
    class FakeArmy:
        def total_points(self):return 700
        def fielded_models(self):return (object(),object(),object())
    row=audit_one("x","list.json","Good","test",tmp_path,importer=lambda p:FakeArmy())
    assert row["status"]=="intake_passed"


def test_import_point_mismatch_reported(tmp_path):
    write_fixture(tmp_path)
    class FakeArmy:
        def total_points(self):return 699
        def fielded_models(self):return (object(),object(),object())
    row=audit_one("x","list.json","Good","test",tmp_path,importer=lambda p:FakeArmy())
    assert "imported_points_mismatch" in row["issues"]


def test_import_model_mismatch_reported(tmp_path):
    write_fixture(tmp_path)
    class FakeArmy:
        def total_points(self):return 700
        def fielded_models(self):return (object(),)
    row=audit_one("x","list.json","Good","test",tmp_path,importer=lambda p:FakeArmy())
    assert "imported_models_mismatch" in row["issues"]


def test_duplicate_calibration_not_approved(tmp_path):
    result=audit_cohort(tmp_path)
    assert result["calibration_anchors_approved"] is False
    assert result["production_scoring_modified"] is False


def test_exact_six_manifest_filenames():
    assert FIXTURES["five_armies"][0]=="five_armies_cal.json"
    assert len(FIXTURES)==6


def test_option_assignments_preserved(tmp_path):
    path=write_fixture(tmp_path)
    data=json.loads(path.read_text())
    data["warbands"][0]["hero"]["options"]=[{"id":"OPT0001","name":"Mount","quantity":1}]
    path.write_text(json.dumps(data))
    row=inspect_fixture(path)
    assert row["option_assignments"][0]["option_id"]=="OPT0001"


def test_invalid_unit_quantity_rejected(tmp_path):
    path=write_fixture(tmp_path)
    data=json.loads(path.read_text())
    data["warbands"][0]["units"][0]["quantity"]=0
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="quantity"):
        inspect_fixture(path)
