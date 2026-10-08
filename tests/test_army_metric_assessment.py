from army_metric_assessment import assess_army_metrics
from army_metrics_entity import ArmyMetrics
from analysis_loader import load_metric_thresholds
from army_metrics_entity import (
    ArmyMetrics,
)

def test_assess_army_metrics_can_override_shooting_value():
    metric_thresholds = load_metric_thresholds()

    densities = ArmyMetrics(
        offence=1.0,
        defence=1.0,
        mobility=1.0,
        magic=1.0,
        shooting=0.07,
        courage=1.0,
        control=1.0,
        command=1.0,
        objective=1.0,
        hero_hunting=1.0,
    )

    assessments = assess_army_metrics(
        densities,
        metric_thresholds,
        shooting_value=0.22,
    )

    shooting = next(
        assessment
        for assessment in assessments
        if assessment.metric == "shooting"
    )

    assert shooting.value == 0.22

def test_assess_army_metrics_can_override_offence_value():
    metric_thresholds = load_metric_thresholds()

    densities = ArmyMetrics(
        offence=9.0,
        defence=0.0,
        mobility=0.0,
        magic=0.0,
        shooting=0.0,
        courage=0.0,
        control=0.0,
        command=0.0,
        objective=0.0,
        hero_hunting=0.0,
    )

    assessments = assess_army_metrics(
        densities,
        metric_thresholds,
        offence_value=0.75,
    )

    offence = next(
        assessment
        for assessment in assessments
        if assessment.metric == "offence"
    )

    assert offence.value == 0.75