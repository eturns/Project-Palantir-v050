"""
Project Palantír
================

File:
    profile_option_state_effect_loader.py

Purpose:
    Loads scalar configured-state effects for Profile Options.

Created:
    DEV-060I1 – Configured State Effect Loader
"""

import csv

from configured_state_effect import ConfiguredStateEffect
from profile_classification import (
    HeroicStatus,
    ModelType,
)
from profile_option import ProfileOption


def _optional_int(value: str | None) -> int | None:
    text = (value or "").strip()

    if not text:
        return None

    return int(text)


def _defence_modifier(value: str | None) -> int:
    text = (value or "").strip()

    if not text:
        return 0

    return int(text)


def _optional_model_type(
    value: str | None,
) -> ModelType | None:
    text = (value or "").strip()

    if not text:
        return None

    try:
        return ModelType[text.upper()]
    except KeyError as error:
        raise ValueError(
            "Unknown model type override: "
            f"{text}"
        ) from error

def _optional_heroic_status(
    value: str | None,
) -> HeroicStatus | None:
    text = (value or "").strip()

    if not text:
        return None

    try:
        return HeroicStatus[text.upper()]
    except KeyError as error:
        raise ValueError(
            "Unknown heroic status override: "
            f"{text}"
        ) from error

def _optional_text(
    value: str | None,
) -> str | None:
    text = (value or "").strip()

    if not text:
        return None

    return text


def load_profile_option_state_effects(
    profile_options: dict[str, ProfileOption],
    file_path: str = (
        "data/profiles/profile_option_state_effects.csv"
    ),
) -> None:
    """
    Loads scalar ConfiguredStateEffect relationships for
    Profile Options.
    """

    effects_by_option: dict[
        str,
        list[ConfiguredStateEffect],
    ] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            option_id = row["option_id"]

            if option_id not in profile_options:
                raise ValueError(
                    "Unknown Profile Option ID in "
                    "profile_option_state_effects.csv: "
                    f"{option_id}"
                )

            effect = ConfiguredStateEffect(
                movement_override=_optional_int(
                    row.get("movement_override")
                ),
                defence_modifier=_defence_modifier(
                    row.get("defence_modifier")
                ),
                model_type_override=_optional_model_type(
                    row.get("model_type_override")
                ),
                shooting_override=_optional_text(
                    row.get("shooting_override")
                ),
                base_size_override_mm=_optional_int(
                    row.get("base_size_override_mm")
                ),
                heroic_status_override=_optional_heroic_status(
                    row.get("heroic_status_override")
                ),
                might_override=_optional_int(
                    row.get("might_override")
                ),
                will_override=_optional_int(
                    row.get("will_override")
                ),
                fate_override=_optional_int(
                    row.get("fate_override")
                ),
            )

            effects_by_option.setdefault(
                option_id,
                [],
            ).append(effect)

    for option_id, effects in effects_by_option.items():
        option = profile_options[option_id]

        object.__setattr__(
            option,
            "configured_state_effects",
            tuple(effects),
        )