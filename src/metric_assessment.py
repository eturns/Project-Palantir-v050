from metric_classifier import classify_metric

from metric_queries import get_metric_threshold

from metric_assessment_entity import (
    MetricAssessmentEntity,
)

def assess_metric(
    metric: str,
    value: float,
    metric_thresholds,
) -> MetricAssessmentEntity:
    """
    Assesses a battlefield metric.
    """

    threshold = get_metric_threshold(
        metric,
        metric_thresholds,
    )

    rating = classify_metric(
        value,
        threshold,
    )

    return MetricAssessmentEntity(
        metric=metric,
        value=value,
        rating=rating,
    )