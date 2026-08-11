"""
Project Palantír
================

File:
    army_profile_resolver.py

Purpose:
    Resolves optimiser army names into canonical profile pools.

Created:
    DEV-052 – Legal Composition Enumeration
"""

from dol_guldur_compositions import dol_guldur_profiles
from profiles import Profile


def resolve_army_profiles(
    army: str,
    profiles: list[Profile],
) -> tuple[Profile, ...]:
    """
    Returns the canonical profile pool for a supported army.
    """

    if army == "Dol Guldur":
        return dol_guldur_profiles(
            profiles
        )

    raise ValueError(
        f"Unsupported army: {army}"
    )