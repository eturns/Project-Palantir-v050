from types import SimpleNamespace

from desktop_analysis_view_model import (
    build_desktop_analysis_view_model,
)

def test_build_desktop_analysis_view_model_maps_core_result_data():
    strength = SimpleNamespace(
        metric="shooting",
        rating="Strong",
        value=0.71,
    )

    weakness = SimpleNamespace(
        metric="magic",
        rating="Weak",
        value=0.08,
    )

    battlefield = SimpleNamespace(
        strengths=(strength,),
        weaknesses=(weakness,),
    )

    definition = SimpleNamespace(
        name="Test Army",
        points_limit=700,
    )

    army = SimpleNamespace(
        total_points=lambda: 695,
    )

    result = {
        "definition": definition,
        "army": army,
        "analysis": {
            "validation_errors": (),
            "battlefield_assessments": battlefield,
        },
        "scenario_analysis_results": (),
        "evidence_records": (),
    }

    view_model = build_desktop_analysis_view_model(
        result,
    )

    assert view_model["army_name"] == "Test Army"
    assert view_model["total_points"] == 695
    assert view_model["points_limit"] == 700
    assert view_model["is_legal"] is True

    assert view_model["strengths"] == (
        {
            "metric": "Shooting",
            "rating": "Strong",
            "value": 0.71,
        },
    )

    assert view_model["weaknesses"] == (
        {
            "metric": "Magic",
            "rating": "Weak",
            "value": 0.08,
        },
    )

def test_build_desktop_analysis_view_model_maps_scenarios_and_evidence():
    scenario = SimpleNamespace(
        scenario_id="HOLD_GROUND",
        scenario_name="Hold Ground",
        pool=SimpleNamespace(
            value="matched_play",
        ),
        score=0.684,
        demands=(
            SimpleNamespace(
                dimension=SimpleNamespace(
                    value="board_control",
                ),
                capability=0.72,
                intensity=0.80,
            ),
        ),
    )

    evidence = SimpleNamespace(
        mechanic="ranged_wargear_weighting",
        status=SimpleNamespace(
            value="provisional",
        ),
        reason="Weighting has not been independently validated.",
        provenance="dev073_calibration",
    )

    result = {
        "definition": SimpleNamespace(
            name="Test Army",
            points_limit=700,
        ),
        "army": SimpleNamespace(
            total_points=lambda: 695,
        ),
        "analysis": {
            "validation_errors": (),
            "metric_assessments": (
                SimpleNamespace(
                    metric="board_presence",
                    rating="Strong",
                    value=0.68,
                ),
            ),
            "battlefield_assessments": SimpleNamespace(
                strengths=(),
                weaknesses=(),
            ),
        },
        "scenario_analysis_results": (
            scenario,
        ),
        "evidence_records": (
            evidence,
        ),
    }

    view_model = build_desktop_analysis_view_model(
        result,
    )

    assert view_model["metrics"] == (
        {
            "metric": "Board Presence",
            "rating": "Strong",
            "value": 0.68,
        },
    )

    assert view_model["scenarios"] == (
        {
            "scenario_id": "HOLD_GROUND",
            "name": "Hold Ground",
            "pool": "matched_play",
            "score": 0.684,
            "demands": (
                {
                    "dimension": "Board Control",
                    "capability": 0.72,
                    "intensity": 0.80,
                },
            ),
        },
    )

    assert view_model["evidence"] == (
        {
            "mechanic": "Ranged Wargear Weighting",
            "status": "PROVISIONAL",
            "reason": (
                "Weighting has not been independently validated."
            ),
            "provenance": "dev073_calibration",
        },
    )    