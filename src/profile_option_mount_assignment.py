"""
Project Palantír
================

File:
    profile_option_mount_assignment.py

Purpose:
    Represents a Mount granted by a ProfileOption.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

from dataclasses import dataclass

from mount import Mount


@dataclass(frozen=True)
class ProfileOptionMountAssignment:
    """
    Represents a Mount granted by a ProfileOption.
    """

    mount: Mount