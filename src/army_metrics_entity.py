"""
Project Palantír
================

File:
    army_metrics_entity.py

Purpose:
    Represents the calculated battlefield metrics for an Army.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-020 – Army Metrics
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass

# ============================================================================
# Dataclass
# ============================================================================

@dataclass
class ArmyMetrics:
    """
    Represents the battlefield metrics for an army.
    """

    offence: float = 0.0
    defence: float = 0.0
    mobility: float = 0.0
    magic: float = 0.0
    shooting: float = 0.0
    courage: float = 0.0
    control: float = 0.0
    command: float = 0.0
    objective: float = 0.0
    hero_hunting: float = 0.0