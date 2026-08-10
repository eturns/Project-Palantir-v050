"""
Project Palantír
================

File:
    profile_option_platform_assignment.py

Purpose:
    Represents a Platform granted by a ProfileOption.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

from dataclasses import dataclass

from model_platform import Platform


@dataclass(frozen=True)
class ProfileOptionPlatformAssignment:
    """
    Represents a Platform granted by a ProfileOption.
    """

    platform: Platform