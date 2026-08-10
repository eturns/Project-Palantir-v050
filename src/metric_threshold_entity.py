"""
Project Palantír
================

File:
    metric_threshold_entity.py

Purpose:
    Represents the threshold values for a battlefield metric.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-021.5 – Metric Threshold Framework
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricThresholdEntity:
    """
    Represents the threshold values for a battlefield metric.
    """

    metric_id: str

    very_weak: float
    weak: float
    average: float
    strong: float
    exceptional: float