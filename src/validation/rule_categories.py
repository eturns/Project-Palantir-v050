# =====================================
# Imports
# =====================================

from database.rule_category import (
    RuleCategory,
)


# =====================================
# Validation
# =====================================

def validate_rule_categories(
    verbose: bool = False,
) -> None:
    """
    Validate the RuleCategory enumeration.
    """

    categories = list(
        RuleCategory,
    )

    assert categories, (
        "RuleCategory must contain at least one category."
    )

    category_names = [
        category.name
        for category in categories
    ]

    category_values = [
        category.value
        for category in categories
    ]

    assert len(category_names) == len(set(category_names)), (
        "RuleCategory contains duplicate enum names."
    )

    assert len(category_values) == len(set(category_values)), (
        "RuleCategory contains duplicate display values."
    )

    for category in categories:

        assert isinstance(category.name, str), (
            "RuleCategory names must be strings."
        )

        assert category.name.strip(), (
            "RuleCategory names cannot be empty."
        )

        assert isinstance(category.value, str), (
            f"RuleCategory.{category.name} value "
            f"must be a string."
        )

        assert category.value.strip(), (
            f"RuleCategory.{category.name} value "
            f"cannot be empty."
        )

    print()
    print("========== RULE CATEGORIES ==========")
    print(
        f"✓ {len(categories)} rule categories validated"
    )

    if verbose:
        _print_rule_categories(
            categories,
        )


# =====================================
# Verbose output
# =====================================

def _print_rule_categories(
    categories,
) -> None:

    print()

    for category in categories:
        print(
            f"{category.name} -> {category.value}"
        )