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
    *,
    offence_value: float | None = None,
    shooting_value: float | None = None,
) -> list[MetricAssessmentEntity]:
    """
    Assesses every battlefield metric for an army.
    """

    assessments = []  

    for metric in METRIC_NAMES:
        if metric == "offence" and offence_value is not None:
            value = offence_value
        elif metric == "shooting" and shooting_value is not None:
            value = shooting_value
        else:
            value = getattr(densities, metric)

        assessment = assess_metric(
            metric,
            value,
            metric_thresholds,
        )

        assessments.append(
            assessment,
        )

    return assessments