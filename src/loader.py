"""
Project Palantír
================

File:
    loader.py

Purpose:
    Loads MESBG profile data from CSV files.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-004 – Data Layer
"""

# ============================================================================
# Imports
# ============================================================================

import csv

from profiles import Profile


# ============================================================================
# Constants
# ============================================================================

PROFILE_FILES = (
    "data/profiles/dol_guldur_profiles.csv",
    "data/profiles/iron_hills_profiles.csv",
)


# ============================================================================
# Functions
# ============================================================================

def _load_profiles_from_file(
    file_path: str,
) -> list[Profile]:
    profiles = []

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            profiles.append(
                Profile(
                    id=row["id"],
                    name=row["name"],
                    points=int(row["points"]),
                    movement=int(
                        row["movement"].replace('"', "")
                    ),
                    fight=int(row["fight"]),
                    shooting=row["shooting"],
                    strength=int(row["strength"]),
                    defence=int(row["defence"]),
                    attacks=int(row["attacks"]),
                    wounds=int(row["wounds"]),
                    courage=row["courage"],
                    intelligence=row["intelligence"],
                    might=int(row["might"]),
                    will=int(row["will"]),
                    fate=int(row["fate"]),
                    max_in_army=int(row["max_in_army"]),
                )
            )

    return profiles


def load_profile(
    profile_id: str,
) -> Profile:
    """
    Loads a single profile from the canonical profile database.
    """

    for profile in load_all_profiles():
        if profile.id == profile_id:
            return profile

    raise ValueError(
        f"Profile '{profile_id}' not found."
    )


def load_all_profiles() -> list[Profile]:
    """
    Loads every profile from the canonical profile database.
    """

    profiles = []
    profile_ids = set()

    for file_path in PROFILE_FILES:
        loaded_profiles = _load_profiles_from_file(
            file_path,
        )

        for profile in loaded_profiles:
            if profile.id in profile_ids:
                raise ValueError(
                    f"Duplicate Profile ID: {profile.id}"
                )

            profile_ids.add(profile.id)
            profiles.append(profile)

    return profiles