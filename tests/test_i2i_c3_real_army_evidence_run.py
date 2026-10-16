"""C3-D runner safety tests; no synthetic outputs are labelled real runs."""
import hashlib
from fractions import Fraction
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

# This test file belongs in tests/, while the runner belongs at repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i2i_c3_real_army_evidence_run import (
    validate_paths, build_evidence_document, normalise_raw_shooting_for_extractor,
)


def test_missing_input_rejected(tmp_path):
    with pytest.raises(ValueError, match="existing JSON"):
        validate_paths(tmp_path / "absent.json", tmp_path / "result.json")


def test_non_json_rejected(tmp_path):
    f = tmp_path / "army.txt"
    f.write_text("dummy")
    with pytest.raises(ValueError, match="existing JSON"):
        validate_paths(f, tmp_path / "result.json")


def test_refuses_overwrite(tmp_path):
    f = tmp_path / "army.json"
    f.write_text("{}")
    with pytest.raises(ValueError, match="new and distinct"):
        validate_paths(f, f)
    out = tmp_path / "result.json"
    out.write_text("existing")
    with pytest.raises(ValueError, match="new and distinct"):
        validate_paths(f, out)


def test_valid_paths(tmp_path):
    f = tmp_path / "army.json"
    f.write_text("{}")
    assert validate_paths(f, tmp_path / "result.json")[0] == f.resolve()


def test_rejects_invalid_army_before_collection(tmp_path):
    f = tmp_path / "army.json"
    f.write_text("{}")
    invalid = {"analysis": {"validation_errors": ["invalid roster"]}}
    with pytest.raises(ValueError, match="Invalid reference army"):
        build_evidence_document(fixture=f, army_key="invalid",
                                result=invalid, analysis_commit="abc",
                                raw_shooting=0.1)


def test_output_provenance_and_no_scoring(tmp_path):
    from unified_capability_inventory import METRIC_NAMES
    f = tmp_path / "army.json"
    f.write_text('{"test": true}')
    metrics = [SimpleNamespace(metric=metric, value=0.4) for metric in METRIC_NAMES]
    analysis = {"validation_errors": (), "metric_assessments": metrics,
                "mechanical_defence": {"combat_density": 0.5, "engagements": 3},
                "mechanical_mobility": None, "mechanical_magic": None,
                "mechanical_courage": None}
    result = {"analysis": analysis,
              "army": SimpleNamespace(total_points=lambda: 700, model_count=lambda: 11),
              "definition": SimpleNamespace(name="Fixture army", points_limit=700)}
    data = build_evidence_document(fixture=f, army_key="fixture", result=result,
                                   analysis_commit="test-commit", raw_shooting=0.15)
    assert len(data["measurements"]) == 10
    assert data["available_count"] == 3
    assert data["roster_sha256"] == hashlib.sha256(f.read_bytes()).hexdigest()
    assert data["reference_anchors_approved"] is False
    assert data["production_scoring_enabled"] is False
    assert data["scenario_scoring_changed"] is False


def test_exact_fraction_shooting_is_converted_without_normalisation():
    assert normalise_raw_shooting_for_extractor(Fraction(3, 20)) == 0.15
    assert normalise_raw_shooting_for_extractor(Fraction(0, 1)) == 0.0


def test_invalid_shooting_is_rejected():
    with pytest.raises(TypeError, match="Fraction or number"):
        normalise_raw_shooting_for_extractor("0.5")
    with pytest.raises(ValueError, match="finite"):
        normalise_raw_shooting_for_extractor(float("nan"))


def test_fraction_accepted_by_evidence_document(tmp_path):
    from unified_capability_inventory import METRIC_NAMES
    f = tmp_path / "army.json"
    f.write_text('{}')
    metrics = [SimpleNamespace(metric=m, value=0.4) for m in METRIC_NAMES]
    analysis = {"validation_errors": (), "metric_assessments": metrics,
                "mechanical_defence": {"combat_density": 0.5, "engagements": 3},
                "mechanical_mobility": None, "mechanical_magic": None,
                "mechanical_courage": None}
    result = {"analysis": analysis,
              "army": SimpleNamespace(total_points=lambda: 700, model_count=lambda: 11),
              "definition": SimpleNamespace(name="Fixture army", points_limit=700)}
    doc = build_evidence_document(fixture=f, army_key="fixture", result=result,
                                  analysis_commit="test-commit", raw_shooting=Fraction(3, 20))
    shooting = next(m for m in doc["measurements"] if m["metric"] == "shooting")
    assert shooting["value"] == 0.15
    assert doc["production_scoring_enabled"] is False
