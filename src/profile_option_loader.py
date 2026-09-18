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
from profile_option_profile_assignment import (
    ProfileOptionProfileAssignment,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)

# ============================================================================
# Functions
# ============================================================================

def load_profile_options(
    profiles: dict[str, Profile],
    file_path: str = "data/profiles/profile_options.csv",
    skip_unknown_profiles: bool = False,
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
                if skip_unknown_profiles:
                    continue

                raise ValueError(
                    f"Unknown Profile ID in profile_options.csv: "
                    f"{profile_id}"
                )

            external_id = (
                row["external_id"].strip()
                if row["external_id"].strip()
                else None
            )

            assigned_profile_ids = tuple(
                profile_id.strip()
                for profile_id in (
                    row.get(
                        "assigned_profile_ids",
                        "",
                    )
                    or ""
                ).split("|")
                if profile_id.strip()
            )

            assigned_relationship_types = tuple(
                relationship_type.strip()
                for relationship_type in (
                    row.get(
                        "assigned_relationship_types",
                        "",
                    )
                    or ""
                ).split("|")
            )

            option = ProfileOption(
                id=row["id"],
                name=row["name"],
                points=int(row["points"]),
                external_id=external_id,
                profile_assignments=tuple(
                    ProfileOptionProfileAssignment(
                        profile_id=assigned_profile_id,
                        relationship_type=(
                            FieldedModelRelationshipType(
                                assigned_relationship_types[index]
                            )
                            if (
                                index < len(assigned_relationship_types)
                                and assigned_relationship_types[index]
                            )
                            else None
                        ),
                    )
                    for index, assigned_profile_id
                    in enumerate(assigned_profile_ids)
                ),
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