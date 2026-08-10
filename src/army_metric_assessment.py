from metric_constants import (
    METRIC_NAMES,
    METRIC_LABELS,
)

from metric_assessment import (
    assess_metric,
)

from metric_assessment_entity import (
    MetricAssessmentEntity,
)

def assess_army_metrics(
    densities,
    metric_thresholds,
) -> list[MetricAssessmentEntity]:
    """
    Assesses every battlefield metric for an army.
    """

    assessments = []  

    for metric in METRIC_NAMES:
        value = getattr(
        densities,
        metric,
    )

        assessment = assess_metric(
            metric,
            value,
            metric_thresholds,
        )

        assessments.append(
            assessment,
        )

    return assessments