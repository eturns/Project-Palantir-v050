"""
Project Palantír
================

File:
    wargear_loader.py

Purpose:
    Loads reusable Wargear entities from CSV data.

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

from wargear import Wargear


# ============================================================================
# Functions
# ============================================================================

def load_wargear(
    file_path: str = "data/wargear/wargear.csv",
) -> dict[str, Wargear]:
    """
    Loads all Wargear entities indexed by their Palantír ID.
    """

    wargear_by_id: dict[str, Wargear] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            wargear = Wargear(
                id=row["id"],
                name=row["name"],
            )

            if wargear.id in wargear_by_id:
                raise ValueError(
                    f"Duplicate Wargear ID: {wargear.id}"
                )

            wargear_by_id[wargear.id] = wargear

    return wargear_by_id


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    loaded_wargear = load_wargear()

    print(
        f"{len(loaded_wargear)} Wargear entities loaded."
    )