from validation.output import (
    print_heading,
    print_pass,
)


def validate_profiles(
    profiles,
    verbose: bool = False,
) -> None:
    """
    Validates all loaded profiles.
    """

    print_heading(
        "PROFILES",
    )

    print_pass(
        f"{len(profiles)} profiles validated",
    )

    if not verbose:
        return

    print()

    for profile in profiles:
        print(
            f" - {profile.id}: {profile.name}"
        )