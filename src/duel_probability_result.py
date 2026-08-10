"""
Project Palantír
================

File:
    duel_probability_result.py

Purpose:
    Represents the calculated outcome probabilities for a Duel.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-039 – Combat Engine Foundation
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass


# ============================================================================
# Classes
# ============================================================================

@dataclass
class DuelProbabilityResult:
    """
    Represents the possible outcomes of a Duel.
    """

    attacker_win_probability: float
    defender_win_probability: float
    draw_probability: float