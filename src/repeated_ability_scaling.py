"""
Project Palantír
================

File:
    repeated_ability_scaling.py

Purpose:
    Provides scaling functions for abilities repeated across an Army.

Version:
    0.3.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-038 – Repeated Ability Scaling
"""

# ============================================================================
# Imports
# ============================================================================

from math import sqrt
from army import Army


# ============================================================================
# Functions
# ============================================================================

def diminishing_returns_multiplier(
    quantity: int,
) -> float:
    """
    Returns a square-root multiplier for repeated abilities.
    """

    if quantity < 1:
        return 0.0

    return sqrt(quantity)


def count_models_with_special_rule(
    army: Army,
    rule_id: str,
) -> int:
    """
    Counts how many models in an Army possess a given Special Rule.
    """

    total = 0

    for entry in army.entries:

        has_rule = any(
            assignment.rule.id == rule_id
            for assignment in entry.profile.special_rules
        )

        if has_rule:
            total += entry.quantity

    return total


def highest_special_rule_parameter(
    army: Army,
    rule_id: str,
) -> int | None:
    """
    Returns the highest parameter for a Special Rule
    possessed by any model in the Army.
    """

    highest_parameter = None

    for entry in army.entries:

        for assignment in entry.profile.special_rules:

            if (
                assignment.rule.id == rule_id
                and assignment.parameter is not None
            ):
                if (
                    highest_parameter is None
                    or assignment.parameter > highest_parameter
                ):
                    highest_parameter = assignment.parameter

    return highest_parameter


def count_models_with_parameterised_special_rule(
    army: Army,
    rule_id: str,
) -> int:
    """
    Counts models possessing a parameterised Special Rule.
    """

    total = 0

    for entry in army.entries:

        has_rule = any(
            assignment.rule.id == rule_id
            and assignment.parameter is not None
            for assignment in entry.profile.special_rules
        )

        if has_rule:
            total += entry.quantity

    return total