"""P2-C3-D: narrow insight wrapping and frozen six-army display invariance."""
import json
from pathlib import Path

import pytest

from desktop_app import (
    _panel_safe_insight_text,
    build_strengths_summary,
    build_weaknesses_summary,
)
from provisional_calibration import load_reference, rate_display


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "calibration" / "provisional_six_army_v2.json"


def test_sidebar_wraps_long_header_and_metrics():
    original = (
        "At or above 0.75 in frozen cohort:\n"
        "• Army Survival Density: 0.872\n"
        "• Stationary Shooting: 1.000\n"
        "Relative only; not scenario scoring"
    )
    output = _panel_safe_insight_text(original, columns=23)
    assert all(len(line) <= 23 for line in output.splitlines())
    assert "0.872" in output
    assert "1.000" in output
    assert "not scenario scoring" in output.replace("\n", " ")
    assert "• " in output


def test_sidebar_formatter_does_not_modify_results():
    vm = {
        "provisional_capabilities": {
            "display_only": True,
            "production_scoring_changed": False,
            "defence_independent_composite_weighting_allowed": False,
            "metrics": (
                {"label": "Army Survival Density", "rating": .872, "status": "evaluated"},
                {"label": "Magic", "rating": None, "status": "not_evaluated"},
            ),
        }
    }
    previous = build_strengths_summary(vm)
    formatted = _panel_safe_insight_text(previous)
    assert "Magic" not in formatted
    assert previous == build_strengths_summary(vm)
    assert "Army Survival Density" in previous


def test_negative_width_rejected():
    with pytest.raises(ValueError):
        _panel_safe_insight_text("Text", columns=5)


def test_all_six_armies_reproduce_frozen_v2_measures():
    reference = load_reference(REFERENCE)
    assert len(reference["armies"]) == 6
    for key, metric in reference["metrics"].items():
        assert metric["mapping_method"] == "zero_to_frozen_maximum"
        maximum = metric["maximum"]
        for army in reference["armies"]:
            raw = metric["reference_raw_values"][army]
            result = rate_display(key, raw, reference)
            assert result.status == "evaluated"
            assert result.raw_value == pytest.approx(raw)
            assert result.rating == pytest.approx(raw / maximum, abs=1e-12)
            assert result.clipped is False


def test_reference_zero_and_above_maximum_are_distinct():
    reference = load_reference(REFERENCE)
    key = "offence_density"
    maximum = reference["metrics"][key]["maximum"]
    zero = rate_display(key, 0.0, reference)
    above = rate_display(key, maximum * 1.2, reference)
    missing = rate_display(key, None, reference)
    assert zero.rating == 0.0 and zero.status == "evaluated"
    assert above.rating == 1.0 and above.clipped
    assert above.raw_value == pytest.approx(maximum * 1.2)
    assert missing.rating is None and missing.status == "not_evaluated"


def test_conditional_is_not_zero():
    reference = load_reference(REFERENCE)
    result = rate_display("stationary_shooting", 0.0, reference, evidence_status="conditional")
    assert result.rating is None
    assert result.status == "conditional"
