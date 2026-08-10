"""
Project Palantír
================

File:
    profile_default_wargear_loader.py

Purpose:
    Loads default Wargear relationships for Profiles.

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

import csv

from profiles import Profile
from wargear import Wargear


# ============================================================================
# Functions
# ============================================================================

def load_profile_default_wargear(
    profiles: dict[str, Profile],
    wargear: dict[str, Wargear],
    file_path: str = (
        "data/profiles/profile_default_wargear.csv"
    ),
) -> None:
    """
    Loads the default Wargear owned by each Profile.
    """

    for profile in profiles.values():
        profile.default_wargear.clear()

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            profile_id = row["profile_id"]
            wargear_id = row["wargear_id"]

            if profile_id not in profiles:
                raise ValueError(
                    "Unknown Profile ID in "
                    "profile_default_wargear.csv: "
                    f"{profile_id}"
                )

            if wargear_id not in wargear:
                raise ValueError(
                    "Unknown Wargear ID in "
                    "profile_default_wargear.csv: "
                    f"{wargear_id}"
                )

            profile = profiles[profile_id]
            selected_wargear = wargear[wargear_id]

            if selected_wargear in profile.default_wargear:
                raise ValueError(
                    "Duplicate default Wargear assignment: "
                    f"{profile_id} -> {wargear_id}"
                )

            profile.default_wargear.append(
                selected_wargear
            )