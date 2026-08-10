"""
Project Palantír
================

File:
    profile_option.py

Purpose:
    Defines a selectable option available to a Profile.

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
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
)
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from profile_option_platform_assignment import (
    ProfileOptionPlatformAssignment,
)
# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class ProfileOption:
    """
    Represents one legal option that may be selected for a Profile.

    The option describes the purchasable package rather than the
    individual Wargear entities it may later grant or remove.
    """

    id: str
    name: str
    points: int
    external_id: str | None = None
    wargear_assignments: tuple[
        ProfileOptionWargearAssignment,
        ...,
    ] = ()
    mount_assignments: tuple[
        ProfileOptionMountAssignment,
        ...
    ] = ()
    platform_assignments: tuple[
        ProfileOptionPlatformAssignment,
        ...
    ] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Profile option ID cannot be empty.")

        if not self.name.strip():
            raise ValueError("Profile option name cannot be empty.")

        if self.points < 0:
            raise ValueError("Profile option points cannot be negative.")

        if (
            self.external_id is not None
            and not self.external_id.strip()
        ):
            raise ValueError(
                "Profile option external ID cannot be empty."
            )


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("profile option module loaded successfully.")
    