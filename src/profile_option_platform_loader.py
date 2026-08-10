"""
Project Palantír
================

File:
    profile_option_platform_loader.py

Purpose:
    Loads Platform assignments for ProfileOptions.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

import csv

from model_platform import Platform
from profile_option import ProfileOption
from profile_option_platform_assignment import (
    ProfileOptionPlatformAssignment,
)


def load_profile_option_platform_assignments(
    profile_options: dict[str, ProfileOption],
    platforms: dict[str, Platform],
    file_path: str = (
        "data/profiles/profile_option_platform.csv"
    ),
) -> None:
    """
    Loads Platform relationships for ProfileOptions.
    """

    assignments_by_option: dict[
        str,
        list[ProfileOptionPlatformAssignment],
    ] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            option_id = row["option_id"]
            platform_id = row["platform_id"]

            if option_id not in profile_options:
                raise ValueError(
                    "Unknown Profile Option ID in "
                    "profile_option_platform.csv: "
                    f"{option_id}"
                )

            if platform_id not in platforms:
                raise ValueError(
                    "Unknown Platform ID in "
                    "profile_option_platform.csv: "
                    f"{platform_id}"
                )

            assignments_by_option.setdefault(
                option_id,
                [],
            ).append(
                ProfileOptionPlatformAssignment(
                    platform=platforms[platform_id],
                )
            )

    for option_id, assignments in (
        assignments_by_option.items()
    ):
        option = profile_options[option_id]

        object.__setattr__(
            option,
            "platform_assignments",
            tuple(assignments),
        )