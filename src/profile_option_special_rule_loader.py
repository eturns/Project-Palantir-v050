"""
Project Palantír
================

File:
    profile_option_special_rule_loader.py

Purpose:
    Loads Special Rule grants and removals for Profile Options.

Created:
    DEV-060I2 – Profile Option Special Rule Loader
"""

import csv

from configured_state_effect import ConfiguredStateEffect
from profile_option import ProfileOption
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule


def _optional_parameter(
    value: str | None,
) -> int | str | None:
    text = (value or "").strip()

    if not text:
        return None

    try:
        return int(text)
    except ValueError:
        return text


def load_profile_option_special_rules(
    profile_options: dict[str, ProfileOption],
    special_rules: dict[str, SpecialRule],
    file_path: str = (
        "data/profiles/profile_option_special_rules.csv"
    ),
) -> None:
    """
    Loads Special Rule grants and removals for Profile Options.
    """

    granted_by_option: dict[
        str,
        list[ProfileSpecialRuleAssignment],
    ] = {}

    removed_by_option: dict[
        str,
        list[str],
    ] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            option_id = row["option_id"]
            rule_id = row["rule_id"]
            action = row["action"].strip().lower()

            if option_id not in profile_options:
                raise ValueError(
                    "Unknown Profile Option ID in "
                    "profile_option_special_rules.csv: "
                    f"{option_id}"
                )

            if rule_id not in special_rules:
                raise ValueError(
                    "Unknown Special Rule ID in "
                    "profile_option_special_rules.csv: "
                    f"{rule_id}"
                )

            if action == "grant":
                assignment = ProfileSpecialRuleAssignment(
                    rule=special_rules[rule_id],
                    parameter=_optional_parameter(
                        row.get("parameter")
                    ),
                )

                granted_by_option.setdefault(
                    option_id,
                    [],
                ).append(assignment)

            elif action == "remove":
                removed_by_option.setdefault(
                    option_id,
                    [],
                ).append(rule_id)

            else:
                raise ValueError(
                    "Unknown Profile Option Special Rule "
                    f"action: {action}"
                )

    affected_option_ids = (
        set(granted_by_option)
        | set(removed_by_option)
    )

    for option_id in affected_option_ids:
        option = profile_options[option_id]

        rule_effect = ConfiguredStateEffect(
            granted_special_rules=tuple(
                granted_by_option.get(
                    option_id,
                    [],
                )
            ),
            removed_special_rule_ids=tuple(
                removed_by_option.get(
                    option_id,
                    [],
                )
            ),
        )

        object.__setattr__(
            option,
            "configured_state_effects",
            (
                *option.configured_state_effects,
                rule_effect,
            ),
        )