"""
Project Palantír
================

File:
    analysis.py

Purpose:
    Represents the analysis of an MESBG army.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-009 – Army Analysis
"""

from dataclasses import dataclass, field

@dataclass
class ArmyAnalysis:
    """
    Represents the analysis of an army.
    """

    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)