"""
Project Palantír
================

File:
    profile_option_wargear_assignment.py

Purpose:
    Defines relationships between Profile Options and Wargear.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043B – Profile Wargear and Option Foundation
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass
from enum import Enum

from wargear import Wargear


# ============================================================================
# Enumerations
# ============================================================================

class WargearAssignmentAction(Enum):
    """
    Describes how a Profile Option affects a Wargear item.
    """

    GRANT = "grant"
    REMOVE = "remove"


# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class ProfileOptionWargearAssignment:
    """
    Represents one Wargear change made by a Profile Option.
    """

    wargear: Wargear
    action: WargearAssignmentAction