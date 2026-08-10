"""
Project Palantír
================

File:
    model_platform_loader.py

Purpose:
    Loads canonical Platform entities from CSV data.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

import csv

from model_platform import Platform, PlatformType


def load_platforms(
    file_path: str = "data/platforms/platforms.csv",
) -> dict[str, Platform]:
    """
    Loads Platform entities indexed by their internal IDs.
    """

    platforms: dict[str, Platform] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            try:
                platform_type = PlatformType(
                    row["platform_type"]
                )
            except ValueError as error:
                raise ValueError(
                    "Unknown Platform type: "
                    f"{row['platform_type']}"
                ) from error

            platform = Platform(
                id=row["id"],
                name=row["name"],
                platform_type=platform_type,
            )

            if platform.id in platforms:
                raise ValueError(
                    "Duplicate Platform ID: "
                    f"{platform.id}"
                )

            platforms[platform.id] = platform

    return platforms