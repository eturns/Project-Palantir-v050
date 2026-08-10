from metric_constants import (
    METRIC_IDS,
)

from metric_description_entity import (
    MetricDescriptionEntity,
)


def get_metric_description(
    metric: str,
    metric_descriptions: dict[
        str,
        MetricDescriptionEntity,
    ],
) -> MetricDescriptionEntity:
    """
    Returns the description for a battlefield metric.
    """

    metric_id = METRIC_IDS[metric]

    return metric_descriptions[metric_id]