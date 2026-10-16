"""E1-C: no fabricated ratings, stable presentation and legacy fallback."""
from types import SimpleNamespace
import pytest
from desktop_app import build_capability_analysis_summary, _raw_measurement_bar


def vm(defence=True):
    d={"metrics":(
        {"metric":"Defence","rating":"Strong","value":0.6},
        {"metric":"Shooting","rating":"Weak","value":0.2},
    )}
    if defence:
        d["defence_presentation"]={
            "army_survival_density": {"key":"army_survival_density", "label":"Army Survival Density", "value":2.927,"calibrated":False},
            "per_model_resilience": {"key":"per_model_resilience", "label":"Per-Model Resilience", "value":0.525,"calibrated":False},
            "engagements":3,
            "benchmark":{"fight":4,"strength":4,"defence":6},
        }
    return d


def test_new_readings_replace_legacy_visible_defence():
    text=build_capability_analysis_summary(vm())
    assert "Army Survival Density" in text
    assert "Per-Model Resilience" in text
    assert "Defence        " not in text
    assert "Shooting" in text
    assert "UNCALIBRATED" in text
    assert text.count("█")>0


def test_no_ratings_attached_to_new_measures():
    text=build_capability_analysis_summary(vm())
    for line in text.splitlines():
        if "Army Survival Density" in line or "Per-Model Resilience" in line:
            assert "Strong" not in line and "Weak" not in line
            assert "Strong" not in line and "Weak" not in line


def test_legacy_fallback_still_visible_without_presentation():
    text=build_capability_analysis_summary(vm(False))
    assert "Defence" in text and "Strong" in text


def test_scale_does_not_change_reported_value():
    text=build_capability_analysis_summary(vm())
    assert "2.927 survivors/100pts" in text
    assert "0.525 survival probability" in text


def test_benchmark_and_no_resurrection_visible():
    text=build_capability_analysis_summary(vm())
    assert "F4 S4 D6" in text and "3 engagements" in text
    assert "resurrection excluded" in text.lower()


def test_negative_and_nan_values_rejected():
    for bad in (-1,float("nan"),float("inf")):
        with pytest.raises(ValueError):
            _raw_measurement_bar(bad, display_max=1)


def test_uncalibrated_required():
    d=vm();d["defence_presentation"]["per_model_resilience"]["calibrated"]=True
    with pytest.raises(ValueError):build_capability_analysis_summary(d)


def test_legacy_summary_not_mutated():
    d=vm();before=d["metrics"]
    build_capability_analysis_summary(d)
    assert d["metrics"] is before
