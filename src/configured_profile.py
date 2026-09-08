"""
Project Palantír
================

File:
    configured_profile.py

Purpose:
    Represents a Profile with selected legal options.

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

from dataclasses import dataclass
from profile_classification import ModelType
from profile_option import ProfileOption
from profiles import Profile
from profile_option_wargear_assignment import (
    WargearAssignmentAction,
)
from wargear import Wargear
from mount import Mount
from model_platform import Platform
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class ConfiguredProfile:
    """
    Represents one Profile with its selected options.

    The underlying Profile remains canonical. Option points are added
    only when evaluating this configured instance.
    """

    profile: Profile
    selected_options: tuple[ProfileOption, ...] = ()

    def __post_init__(self) -> None:
        illegal_options = tuple(
            option
            for option in self.selected_options
            if option not in self.profile.profile_options
        )

        if illegal_options:
            raise ValueError(
                "Configured Profile contains an option "
                "that is not legal for its Profile."
            )

        selected_option_ids = tuple(
            option.id
            for option in self.selected_options
        )

        if len(selected_option_ids) != len(
            set(selected_option_ids)
        ):
            raise ValueError(
                "Configured Profile cannot select "
                "the same option more than once."
            )

    @property
    def points(self) -> int:
        """
        Returns the Profile's base points plus all selected option costs.
        """

        return self.profile.points + sum(
            option.points
            for option in self.selected_options
        )

    @property
    def effective_wargear(self) -> tuple[Wargear, ...]:
        """
        Returns the Profile's final Wargear after applying
        all selected option assignments.
        """

        wargear_by_id = {
            wargear.id: wargear
            for wargear in self.profile.default_wargear
        }

        for option in self.selected_options:
            for assignment in option.wargear_assignments:
                if (
                    assignment.action
                    == WargearAssignmentAction.REMOVE
                ):
                    wargear_by_id.pop(
                        assignment.wargear.id,
                        None,
                    )

                elif (
                    assignment.action
                    == WargearAssignmentAction.GRANT
                ):
                    wargear_by_id[
                        assignment.wargear.id
                    ] = assignment.wargear

        return tuple(wargear_by_id.values())  

    @property
    def effective_mount(self) -> Mount | None:
        """
        Returns the Mount used by this configured Profile.
        """

        option_mounts = [
            assignment.mount
            for option in self.selected_options
            for assignment in option.mount_assignments
        ]

        if len(option_mounts) > 1:
            raise ValueError(
                "Configured Profile cannot have more than "
                "one Mount."
            )

        if option_mounts:
            return option_mounts[0]

        return self.profile.default_mount

    @property
    def effective_platform(self) -> Platform | None:
        """
        Returns the Platform used by this configured Profile.
        """

        option_platforms = [
            assignment.platform
            for option in self.selected_options
            for assignment in option.platform_assignments
        ]

        if len(option_platforms) > 1:
            raise ValueError(
                "Configured Profile cannot have more than "
                "one Platform."
            )

        if option_platforms:
            return option_platforms[0]

        return None

    @property
    def effective_movement(self) -> int:
        """
        Returns the Profile's effective Movement after applying
        selected configured-state effects.
        """

        movement_overrides = [
            effect.movement_override
            for option in self.selected_options
            for effect in option.configured_state_effects
            if effect.movement_override is not None
        ]

        if len(movement_overrides) > 1:
            raise ValueError(
                "Configured Profile cannot have more than "
                "one Movement override."
            )

        if movement_overrides:
            return movement_overrides[0]

        return self.profile.movement

    @property
    def effective_base_size_mm(self) -> int:
        """
        Returns the effective base size after applying configured-state
        overrides, Mount configuration, and the base Profile value.
        """

        base_size_overrides = [
            effect.base_size_override_mm
            for option in self.selected_options
            for effect in option.configured_state_effects
            if effect.base_size_override_mm is not None
        ]

        if len(base_size_overrides) > 1:
            raise ValueError(
                "Configured Profile cannot have more than "
                "one base-size override."
            )

        if base_size_overrides:
            return base_size_overrides[0]

        if self.effective_mount is not None:
            return self.effective_mount.base_size_mm

        return self.profile.base_size_mm

    @property
    def effective_defence(self) -> int:
        """
        Returns the Profile's effective Defence after applying
        selected configured-state modifiers.
        """

        defence_modifier = sum(
            effect.defence_modifier
            for option in self.selected_options
            for effect in option.configured_state_effects
        )

        return (
            self.profile.defence
            + defence_modifier
        )

    @property
    def effective_model_types(self) -> set[ModelType]:
        """
        Returns the Profile's effective model types after applying
        selected configured-state overrides.
        """

        model_type_overrides = [
            effect.model_type_override
            for option in self.selected_options
            for effect in option.configured_state_effects
            if effect.model_type_override is not None
        ]

        if len(model_type_overrides) > 1:
            raise ValueError(
                "Configured Profile cannot have more than "
                "one model type override."
            )

        if model_type_overrides:
            return {
                model_type_overrides[0]
            }

        return set(
            self.profile.model_types
        )

    @property
    def effective_shooting(self) -> str:
        """
        Returns the Profile's effective shooting value after applying
        selected configured-state overrides.
        """

        shooting_overrides = [
            effect.shooting_override
            for option in self.selected_options
            for effect in option.configured_state_effects
            if effect.shooting_override is not None
        ]

        if len(shooting_overrides) > 1:
            raise ValueError(
                "Configured Profile cannot have more than "
                "one shooting override."
            )

        if shooting_overrides:
            return shooting_overrides[0]

        return self.profile.shooting

    @property
    def effective_special_rules(
        self,
    ) -> list[ProfileSpecialRuleAssignment]:
        """
        Returns the Profile's effective static Special Rules after
        applying removals and grants from selected configured-state effects.
        """

        removed_rule_ids = {
            rule_id
            for option in self.selected_options
            for effect in option.configured_state_effects
            for rule_id in effect.removed_special_rule_ids
        }

        effective_rules = [
            assignment
            for assignment in self.profile.special_rules
            if assignment.rule.id not in removed_rule_ids
        ]

        for option in self.selected_options:
            for effect in option.configured_state_effects:
                effective_rules.extend(
                    effect.granted_special_rules
                )

        return effective_rules

def create_configured_profile_from_external_options(
    profile: Profile,
    external_option_ids: tuple[str, ...],
    profile_options_by_external_id: dict[
        str,
        ProfileOption,
    ],
) -> ConfiguredProfile:
    """
    Creates a ConfiguredProfile from external option IDs.
    """

    selected_options: list[ProfileOption] = []

    for external_option_id in external_option_ids:
        if (
            external_option_id
            not in profile_options_by_external_id
        ):
            raise ValueError(
                "Unknown external Profile Option ID: "
                f"{external_option_id}"
            )

        selected_options.append(
            profile_options_by_external_id[
                external_option_id
            ]
        )

    return ConfiguredProfile(
        profile=profile,
        selected_options=tuple(selected_options),
    ) 