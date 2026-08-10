"""
Project Palantír
================

File:
    metric_assessment_entity.py

Purpose:
    Represents the assessment of a battlefield metric.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-022.5 – Metric Assessment
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricAssessmentEntity:
    """
    Represents the assessment of a battlefield metric.
    """

    metric: str
    value: float
    rating: str