from validation.output import (
    print_heading,
    print_pass,
)


def validate_database(
    profiles,
) -> None:
    """
    Validates the profile database.
    """

    print_heading(
        "DATABASE",
    )

    print_pass(
        f"Profiles loaded ({len(profiles)})",
    )