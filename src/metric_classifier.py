from analysis_constants import (
    VERY_WEAK,
    WEAK,
    AVERAGE,
    STRONG,
    EXCEPTIONAL,
)

from metric_threshold_entity import MetricThresholdEntity

def classify_metric(
    value: float,
    thresholds: MetricThresholdEntity,
) -> str:
    """
    Classifies a battlefield metric using the supplied thresholds.
    """

    if value >= thresholds.exceptional:
        return EXCEPTIONAL

    if value >= thresholds.strong:
        return STRONG

    if value >= thresholds.average:
        return AVERAGE

    if value >= thresholds.weak:
        return WEAK

    return VERY_WEAK