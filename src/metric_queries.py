from metric_constants import METRIC_IDS


def get_metric_threshold(
    metric_name: str,
    metric_thresholds,
):
    """
    Returns the threshold object for a battlefield metric.
    """

    metric_id = METRIC_IDS[metric_name]

    return metric_thresholds[metric_id]