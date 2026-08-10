"""
Project Palantír
================

File:
    battlefield_assessment_entity.py

Purpose:
    Represents the strengths and weaknesses of an army.

Version:
    0.2.0-alpha
"""

from dataclasses import dataclass

from metric_assessment_entity import (
    MetricAssessmentEntity,
)


@dataclass(frozen=True)
class BattlefieldAssessmentEntity:
    """
    Represents the assessed strengths and weaknesses
    of an army.
    """

    strengths: list[MetricAssessmentEntity]

    weaknesses: list[MetricAssessmentEntity]