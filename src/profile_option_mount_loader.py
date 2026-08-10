"""
Project Palantír
================

File:
    profile_option_mount_loader.py

Purpose:
    Loads Mount assignments for ProfileOptions.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

import csv

from mount import Mount
from profile_option import ProfileOption
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)


def load_profile_option_mount_assignments(
    profile_options: dict[str, ProfileOption],
    mounts: dict[str, Mount],
    file_path: str = (
        "data/profiles/profile_option_mount.csv"
    ),
) -> None:
    """
    Loads Mount relationships for ProfileOptions.
    """

    assignments_by_option: dict[
        str,
        list[ProfileOptionMountAssignment],
    ] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            option_id = row["option_id"]
            mount_id = row["mount_id"]

            if option_id not in profile_options:
                raise ValueError(
                    "Unknown Profile Option ID in "
                    "profile_option_mount.csv: "
                    f"{option_id}"
                )

            if mount_id not in mounts:
                raise ValueError(
                    "Unknown Mount ID in "
                    "profile_option_mount.csv: "
                    f"{mount_id}"
                )

            assignments_by_option.setdefault(
                option_id,
                [],
            ).append(
                ProfileOptionMountAssignment(
                    mount=mounts[mount_id],
                )
            )

    for option_id, assignments in (
        assignments_by_option.items()
    ):
        option = profile_options[option_id]

        object.__setattr__(
            option,
            "mount_assignments",
            tuple(assignments),
        )