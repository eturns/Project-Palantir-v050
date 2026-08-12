"""
Project Palantír
================

File:
    board_presence_inputs.py

Purpose:
    Represents the objective inputs used to calculate
    Board Presence.

Created:
    DEV-053 – Objective Functions and Weighting
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardPresenceInputs:
    model_presence: float
    manoeuvrability: float
    control: float