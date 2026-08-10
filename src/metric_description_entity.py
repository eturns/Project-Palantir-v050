from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDescriptionEntity:
    """
    Stores the descriptive text for a battlefield metric.
    """

    metric_id: str

    strength_description: str

    weakness_description: str