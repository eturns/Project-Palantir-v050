"""
Project Palantír
================

File:
    profile_option_wargear_loader.py

Purpose:
    Loads Wargear assignments for Profile Options.

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
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from wargear import Wargear


# ============================================================================
# Functions
# ============================================================================

def load_profile_option_wargear_assignments(
    profile_options: dict[str, ProfileOption],
    wargear: dict[str, Wargear],
    file_path: str = (
        "data/profiles/profile_option_wargear.csv"
    ),
) -> None:
    """
    Loads Wargear grants and removals for Profile Options.
    """

    assignments_by_option: dict[
        str,
        list[ProfileOptionWargearAssignment],
    ] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            option_id = row["option_id"]
            wargear_id = row["wargear_id"]
            action_text = row["action"].strip().lower()

            if option_id not in profile_options:
                raise ValueError(
                    "Unknown Profile Option ID in "
                    "profile_option_wargear.csv: "
                    f"{option_id}"
                )

            if wargear_id not in wargear:
                raise ValueError(
                    "Unknown Wargear ID in "
                    "profile_option_wargear.csv: "
                    f"{wargear_id}"
                )

            try:
                action = WargearAssignmentAction(
                    action_text
                )
            except ValueError as error:
                raise ValueError(
                    "Unknown Wargear assignment action: "
                    f"{action_text}"
                ) from error

            assignment = ProfileOptionWargearAssignment(
                wargear=wargear[wargear_id],
                action=action,
            )

            assignments_by_option.setdefault(
                option_id,
                [],
            ).append(assignment)

    for option_id, assignments in assignments_by_option.items():
        option = profile_options[option_id]

        object.__setattr__(
            option,
            "wargear_assignments",
            tuple(assignments),
        )