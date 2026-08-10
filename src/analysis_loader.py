"""
Project Palantír
================

File:
    analysis_loader.py

Purpose:
    Loads Palantír analysis data.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-021.5 – Metric Threshold Framework
"""

import csv

from metric_threshold_entity import MetricThresholdEntity

from metric_description_entity import (
    MetricDescriptionEntity,
)

def load_metric_thresholds() -> dict[str, MetricThresholdEntity]:
    """
    Loads battlefield metric thresholds.
    """

    thresholds: dict[str, MetricThresholdEntity] = {}

    with open(
        "data/analysis/metric_thresholds.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            threshold = MetricThresholdEntity(
                metric_id=row["metric_id"],
                very_weak=float(row["very_weak"]),
                weak=float(row["weak"]),
                average=float(row["average"]),
                strong=float(row["strong"]),
                exceptional=float(row["exceptional"]),
            )

            thresholds[threshold.metric_id] = threshold

    return thresholds

def load_metric_descriptions(
) -> dict[str, MetricDescriptionEntity]:
    """
    Loads battlefield metric descriptions.
    """

    descriptions: dict[
        str,
        MetricDescriptionEntity,
    ] = {}

    with open(
        "data/analysis/metric_descriptions.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            description = MetricDescriptionEntity(
                metric_id=row["metric_id"],
                strength_description=row[
                    "strength_description"
                ],
                weakness_description=row[
                    "weakness_description"
                ],
            )

            descriptions[
                description.metric_id
            ] = description

    return descriptions