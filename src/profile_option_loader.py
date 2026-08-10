"""
Project Palantír
================

File:
    profile_option_loader.py

Purpose:
    Loads Profile Options from CSV data.

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

from profile_option import ProfileOption
from profiles import Profile


# ============================================================================
# Functions
# ============================================================================

def load_profile_options(
    profiles: dict[str, Profile],
    file_path: str = "data/profiles/profile_options.csv",
) -> dict[str, ProfileOption]:
    """
    Loads Profile Options and attaches each option to its legal Profile.
    """

    options_by_id: dict[str, ProfileOption] = {}
    external_ids: set[str] = set()

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            profile_id = row["profile_id"]

            if profile_id not in profiles:
                raise ValueError(
                    f"Unknown Profile ID in profile_options.csv: "
                    f"{profile_id}"
                )

            external_id = (
                row["external_id"].strip()
                if row["external_id"].strip()
                else None
            )

            option = ProfileOption(
                id=row["id"],
                name=row["name"],
                points=int(row["points"]),
                external_id=external_id,
            )

            if option.id in options_by_id:
                raise ValueError(
                    f"Duplicate Profile Option ID: {option.id}"
                )

            if (
                option.external_id is not None
                and option.external_id in external_ids
            ):
                raise ValueError(
                    "Duplicate external Profile Option ID: "
                    f"{option.external_id}"
                )

            options_by_id[option.id] = option

            if option.external_id is not None:
                external_ids.add(option.external_id)

            profiles[profile_id].profile_options.append(option)

    return options_by_id

def build_profile_options_by_external_id(
    profile_options: dict[str, ProfileOption],
) -> dict[str, ProfileOption]:
    """
    Returns Profile Options indexed by their external option ID.

    Options without an external ID are omitted.
    """

    options_by_external_id: dict[str, ProfileOption] = {}

    for option in profile_options.values():
        if option.external_id is None:
            continue

        if option.external_id in options_by_external_id:
            raise ValueError(
                "Duplicate external Profile Option ID: "
                f"{option.external_id}"
            )

        options_by_external_id[
            option.external_id
        ] = option

    return options_by_external_id