def print_heading(title: str) -> None:
    """
    Prints a standard validation heading.
    """

    print()
    print("=" * 10, title, "=" * 10)


def print_pass(name: str) -> None:
    """
    Prints a passing validation.
    """

    print(f"✓ {name}")


def print_fail(name: str) -> None:
    """
    Prints a failing validation
    """

    print(f"✗ {name}")