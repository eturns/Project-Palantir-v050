"""DEV-077S-I2-C-H3-A.

Non-destructive mechanical Defence integration tests.

The existing capability assessments must remain unchanged.
"""

from types import SimpleNamespace

import pytest

from services import army_analysis_service as service


def setup_analysis(monkeypatch):
    army = SimpleNamespace(
        validate=lambda points_limit: [],
    )

    densities = SimpleNamespace(
        defence=0.42,
    )

    existing_assessments = object()
    existing_battlefield = object()
    assessment_calls = []

    monkeypatch.setattr(
        service,
        "calculate_army_metric_densities",
        lambda *_: densities,
    )

    monkeypatch.setattr(
        service,
        "calculate_army_offensive_output_density",
        lambda *_: 0.61,
    )

    monkeypatch.setattr(
        service,
        "calculate_army_shooting_output_density",
        lambda **_: 0.27,
    )

    monkeypatch.setattr(
        service,
        "build_shooting_benchmark_defender",
        lambda: object(),
    )

    monkeypatch.setattr(
        service,
        "normalise_shooting_output_density",
        lambda value: 0.33,
    )

    def fake_assess(
        densities_argument,
        thresholds,
        **kwargs,
    ):
        assessment_calls.append(
            (densities_argument, thresholds, kwargs)
        )
        return existing_assessments

    monkeypatch.setattr(
        service,
        "assess_army_metrics",
        fake_assess,
    )

    monkeypatch.setattr(
        service,
        "assess_battlefield",
        lambda assessments: existing_battlefield,
    )

    # This army stand-in deliberately avoids depending on
    # real combat model construction.
    army.analysis_metrics = lambda: object()

    return (
        army,
        densities,
        existing_assessments,
        existing_battlefield,
        assessment_calls,
    )


def test_analysis_exposes_separate_mechanical_defence(
    monkeypatch,
):
    (
        army,
        densities,
        _,
        _,
        _,
    ) = setup_analysis(monkeypatch)

    expected = {
        "combat_survival": 0.55,
        "combat_density": 0.21,
        "recovery_presence": 0.75,
        "recovery_density": 0.29,
        "engagements": 3,
    }

    # Patch the proposed new calculation boundary.
    monkeypatch.setattr(
        service,
        "calculate_mechanical_defence_diagnostics",
        lambda supplied_army: expected,
        raising=False,
    )

    result = service.analyse_imported_army(
        army,
        army_list=object(),
        points_limit=700,
        metric_thresholds=object(),
    )

    assert result["mechanical_defence"] == expected
    assert result["metric_densities"] is densities


def test_mechanical_defence_does_not_replace_assessments(
    monkeypatch,
):
    (
        army,
        densities,
        existing_assessments,
        existing_battlefield,
        assessment_calls,
    ) = setup_analysis(monkeypatch)

    monkeypatch.setattr(
        service,
        "calculate_mechanical_defence_diagnostics",
        lambda supplied_army: {
            "combat_survival": 0.9,
            "combat_density": 0.8,
            "recovery_presence": 0.95,
            "recovery_density": 0.85,
            "engagements": 3,
        },
        raising=False,
    )

    thresholds = object()

    result = service.analyse_imported_army(
        army,
        army_list=object(),
        points_limit=700,
        metric_thresholds=thresholds,
    )

    assert result["metric_assessments"] is existing_assessments
    assert result["battlefield_assessments"] is existing_battlefield

    assert len(assessment_calls) == 1

    supplied_densities, supplied_thresholds, overrides = (
        assessment_calls[0]
    )

    assert supplied_densities is densities
    assert supplied_thresholds is thresholds

    # Only the established Offence and Shooting overrides
    # should reach the existing assessment pipeline.
    assert overrides == {
        "offence_value": 0.61,
        "shooting_value": 0.33,
    }

    assert densities.defence == pytest.approx(0.42)