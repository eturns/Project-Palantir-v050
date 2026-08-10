"""
Project Palantír
================

File:
    metrics.py

Purpose:
    Calculates objective metrics used for
    army analysis.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-009 – Army Analysis
"""

from dataclasses import dataclass

@dataclass
class AnalysisMetrics:
    """
    Represents calculated metrics for an army.
    """

    might_density: float
    will_density: float
    fate_density: float
    
    profile_density: float
    
    model_count: int
    model_density: float

    average_movement: float

    fast_model_density: float
    standard_model_density: float
    slow_model_density: float

    average_fight: float
    average_strength: float
    average_attacks: float

    high_fight_density: float
    high_strength_density: float

    average_defence: float
    average_wounds: float

    high_defence_density: float
    multi_wound_density: float