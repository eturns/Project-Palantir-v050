"""
Project Palantír
================

File:
    queries.py

Purpose:
    Provides query functions for collections of MESBG profiles.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-005 – Query Engine
"""

# ============================================================================
# Imports
# ============================================================================

from profiles import Profile

# ============================================================================
# Constants
# ============================================================================

# (None yet)

# ============================================================================
# Functions
# ============================================================================

def total_points(profiles: list[Profile]) -> int:
    """
    Calculates the total points value of a collection of profiles.

    Args:
        profiles:
            The profiles to analyse.

    Returns:
        Total points value.
    """

    total = 0

    for profile in profiles:
        total += profile.points

    return total

def highest_value(
    profiles: list[Profile],
    attribute: str,
) -> int:
    """
    Returns the highest value of a chosen attribute.
    """

    highest = 0

    for profile in profiles:

        value = getattr(profile, attribute)

        if value > highest:
            highest = value

    return highest

def profiles_costing(
    profiles: list[Profile],
    points: int,
) -> list[Profile]:
    """
    Returns every profile with the specified points value.
    """

    return profiles_with_value(
        profiles,
        "points",
        points,
    )

def profiles_with_value(
    profiles: list[Profile],
    attribute: str,
    value,
) -> list[Profile]:
    """
    Returns every profile whose chosen attribute equals the supplied value.
    """

    matching_profiles = []

    for profile in profiles:

        if getattr(profile, attribute) == value:
            matching_profiles.append(profile)

    return matching_profiles

def profiles_with_minimum_value(
    profiles: list[Profile],
    attribute: str,
    minimum: int,
) -> list[Profile]:
    """
    Returns every profile whose chosen attribute is at least the supplied value.

    Args:
        profiles:
            Profiles to search.

        attribute:
            The attribute to compare.

        minimum:
            The minimum acceptable value.

    Returns:
        A list of matching Profile objects.
    """

    matching_profiles = []

    for profile in profiles:

        if getattr(profile, attribute) >= minimum:
            matching_profiles.append(profile)

    return matching_profiles

def find_profile(
    profiles: list[Profile],
    profile_id: str,
) -> Profile:
    """
    Returns the Profile with the requested ID.

    Args:
        profiles:
            Profiles to search.

        profile_id:
            The profile ID to locate.

    Returns:
        The matching Profile.

    Raises:
        ValueError:
            If the profile cannot be found.
    """

    for profile in profiles:

        if profile.id == profile_id:
            return profile

    raise ValueError(f"Profile '{profile_id}' not found.")
