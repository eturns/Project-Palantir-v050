"""
Project Palantír
================

File:
    profile_default_mount_loader.py

Purpose:
    Loads inherent Mount relationships for Profiles.

Version:
    0.4.0-alpha

Created:
    DEV-043D – Iron Hills Import Integration
"""

import csv

from mount import Mount
from profiles import Profile


def load_profile_default_mounts(
    profiles: dict[str, Profile],
    mounts: dict[str, Mount],
    file_path: str = (
        "data/profiles/profile_default_mount.csv"
    ),
) -> None:
    """
    Assigns inherent Mounts to Profiles.
    """

    assigned_profile_ids: set[str] = set()

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            profile_id = row["profile_id"]
            mount_id = row["mount_id"]

            if profile_id not in profiles:
                raise ValueError(
                    "Unknown Profile ID in "
                    "profile_default_mount.csv: "
                    f"{profile_id}"
                )

            if mount_id not in mounts:
                raise ValueError(
                    "Unknown Mount ID in "
                    "profile_default_mount.csv: "
                    f"{mount_id}"
                )

            if profile_id in assigned_profile_ids:
                raise ValueError(
                    "Duplicate default Mount assignment "
                    "for Profile ID: "
                    f"{profile_id}"
                )

            assigned_profile_ids.add(profile_id)

            profiles[profile_id].default_mount = (
                mounts[mount_id]
            )