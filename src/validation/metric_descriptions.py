# =====================================
# Validation
# =====================================

def validate_metric_descriptions(
    metric_descriptions,
    verbose: bool = False,
) -> None:
    """
    Validate all metric descriptions.
    """

    assert metric_descriptions, (
        "Metric descriptions must not be empty."
    )

    for metric_id, description in metric_descriptions.items():

        # ---------------------------------
        # Identity
        # ---------------------------------

        assert description.metric_id == metric_id, (
            f"Metric description ID mismatch "
            f"for '{metric_id}'."
        )

        # ---------------------------------
        # Strength description
        # ---------------------------------

        assert isinstance(
            description.strength_description,
            str,
        )

        assert description.strength_description.strip(), (
            f"{metric_id} strength description "
            f"cannot be empty."
        )

        # ---------------------------------
        # Weakness description
        # ---------------------------------

        assert isinstance(
            description.weakness_description,
            str,
        )

        assert description.weakness_description.strip(), (
            f"{metric_id} weakness description "
            f"cannot be empty."
        )

        # ---------------------------------
        # Prevent copy/paste mistakes
        # ---------------------------------

        assert (
            description.strength_description
            != description.weakness_description
        ), (
            f"{metric_id} strength and weakness "
            f"descriptions should differ."
        )

    print()
    print("========== METRIC DESCRIPTIONS ==========")
    print(
        f"✓ {len(metric_descriptions)} "
        f"metric descriptions validated"
    )

    if verbose:
        _print_metric_descriptions(
            metric_descriptions,
        )


# =====================================
# Verbose output
# =====================================

def _print_metric_descriptions(
    metric_descriptions,
) -> None:

    print()

    for description in metric_descriptions.values():
        print(description)