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

from profile_option import ProfileOption
from profiles import Profile
from profile_option_wargear_assignment import (
    WargearAssignmentAction,
)
from wargear import Wargear
from mount import Mount
from model_platform import Platform
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
    def effective_base_size_mm(self) -> int:
        """
        Returns the physical base size used by this configured Profile.
        """

        if self.effective_mount is not None:
            return self.effective_mount.base_size_mm

        return self.profile.base_size_mm


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
    