"""
Project Palantír
================

File:
    army_metric_densities.py

Purpose:
    Calculates battlefield metric densities for an army.

Version:
    0.2.0-alpha

Created:
    DEV-021 – Army Metric Densities
"""

from army import Army
from army_metrics import calculate_army_metrics
from army_metrics_entity import ArmyMetrics
from metric_constants import METRIC_NAMES
from army_list import ArmyList


def calculate_army_metric_densities(
    army: Army,
    army_list : ArmyList
) -> ArmyMetrics:
    """
    Calculates battlefield metric densities
    per 100 army points.
    """

    metrics = calculate_army_metrics(
        army,
        army_list,
    )

    densities = ArmyMetrics()

    army_points = army.total_points()

    if army_points == 0:
        return densities

    for metric in METRIC_NAMES:

        setattr(
            densities,
            metric,
            (
                getattr(metrics, metric)
                * 100
            )
            / army_points,
        )

    return densities