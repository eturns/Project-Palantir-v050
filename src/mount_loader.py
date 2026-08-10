"""
Project Palantír
================

File:
    mount_loader.py

Purpose:
    Loads canonical Mount entities from CSV data.

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


def load_mounts(
    file_path: str = "data/mounts/mounts.csv",
) -> dict[str, Mount]:
    """
    Loads Mount entities indexed by their internal IDs.
    """

    mounts: dict[str, Mount] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            mount = Mount(
                id=row["id"],
                name=row["name"],
            )

            if mount.id in mounts:
                raise ValueError(
                    "Duplicate Mount ID: "
                    f"{mount.id}"
                )

            mounts[mount.id] = mount

    return mounts