"""E1-D: legacy Defence insights hidden only where replacement exists."""
from copy import deepcopy
import pytest
from desktop_app import (
    build_strengths_summary, build_weaknesses_summary,
    build_capability_analysis_summary,
)


def vm(replacement=True):
    d={
        "metrics": (
            {"metric":"Defence", "rating":"Exceptional", "value":3.16},
            {"metric":"Control", "rating":"Strong", "value":3.73},
        ),
        "strengths": (
            {"metric":"Defence", "rating":"Exceptional", "value":3.16},
            {"metric":"Control", "rating":"Exceptional", "value":3.73},
        ),
        "weaknesses": (
            {"metric":"Shooting", "rating":"Weak", "value":0.20},
            {"metric":" defence ", "rating":"Weak", "value":0.10},
        ),
        "scenarios": ({"score":0.8},),
    }
    if replacement:
        d["defence_presentation"]={
            "army_survival_density":{"label":"Army Survival Density","value":1.321,"calibrated":False},
            "per_model_resilience":{"label":"Per-Model Resilience","value":0.841,"calibrated":False},
            "benchmark":{"fight":4,"strength":4,"defence":6},"engagements":3,
        }
    return d


def test_strengths_hide_legacy_defence_only_when_replaced():
    text=build_strengths_summary(vm())
    assert "Defence:" not in text
    assert "Control: Exceptional (3.73)" in text


def test_weaknesses_hide_legacy_defence_case_insensitively():
    text=build_weaknesses_summary(vm())
    assert "defence" not in text.lower()
    assert "Shooting: Weak (0.20)" in text


def test_both_old_summaries_survive_when_replacement_absent():
    data=vm(False)
    assert "Defence: Exceptional" in build_strengths_summary(data)
    assert "defence" in build_weaknesses_summary(data).lower()
    assert "Defence" in build_capability_analysis_summary(data)


def test_empty_filtered_lists_produce_none():
    data=vm()
    data["strengths"]=({"metric":"Defence","rating":"Strong","value":0.2},)
    data["weaknesses"]=({"metric":"Defence","rating":"Weak","value":0.2},)
    assert build_strengths_summary(data)=="• None"
    assert build_weaknesses_summary(data)=="• None"


def test_no_modification_of_original_view_model_or_scenarios():
    data=vm(); original=deepcopy(data)
    build_strengths_summary(data); build_weaknesses_summary(data)
    build_capability_analysis_summary(data)
    assert data==original


def test_insights_preserve_non_defence_order_and_values():
    data=vm()
    data["strengths"]=(
        {"metric":"Magic","rating":"Average","value":1.7},
        *data["strengths"],
        {"metric":"Objective","rating":"Exceptional","value":2.85},
    )
    text=build_strengths_summary(data)
    assert text.splitlines()==[
        "• Magic: Average (1.70)",
        "• Control: Exceptional (3.73)",
        "• Objective: Exceptional (2.85)",
    ]


def test_without_defence_replacement_strengths_original_order():
    data=vm(False)
    text=build_strengths_summary(data)
    assert text.index("Defence") < text.index("Control")
