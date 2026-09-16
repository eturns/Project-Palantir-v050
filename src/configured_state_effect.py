"""
Project Palantír
================

File:
    configured_state_effect.py

Purpose:
    Defines bounded static analysis-relevant effects produced by
    configured Profile options.

Created:
    DEV-060A1 – Configured State Effects Foundation
"""

from dataclasses import dataclass
from profile_classification import (
    HeroicStatus,
    ModelType,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)

@dataclass(frozen=True)
class ConfiguredStateEffect:
    """
    Represents one bounded static configured-state effect.

    DEV-060A1 initially supports only a Movement override.
    Additional static configured effects are added incrementally.
    """

    movement_override: int | None = None
    defence_modifier: int = 0
    model_type_override: ModelType | None = None
    heroic_status_override: HeroicStatus | None = None
    might_override: int | None = None
    will_override: int | None = None
    fate_override: int | None = None
    shooting_override: str | None = None
    granted_special_rules: tuple[
        ProfileSpecialRuleAssignment,
        ...
    ] = ()
    removed_special_rule_ids: tuple[str, ...] = ()
    base_size_override_mm: int | None = None

    def __post_init__(self) -> None:
        if (
            self.movement_override is not None
            and self.movement_override <= 0
        ):
            raise ValueError(
                "Movement override must be greater than zero."
            )
        if (
            self.base_size_override_mm is not None
            and self.base_size_override_mm <= 0
        ):
            raise ValueError(
                "Base-size override must be greater than zero."
            )
        for resource_name, resource_value in (
            ("Might", self.might_override),
            ("Will", self.will_override),
            ("Fate", self.fate_override),
        ):
            if (
                resource_value is not None
                and resource_value < 0
            ):
                raise ValueError(
                    f"{resource_name} override must not be negative."
                )