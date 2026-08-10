from army_rule_metric_calculator import (
    calculate_army_rule_metrics,
)


# =====================================
# Validation
# =====================================

def validate_army_rule_metrics(
    army_rules,
    verbose: bool = False,
) -> None:
    """
    Validate battlefield metrics for every Army Rule.
    """

    assert army_rules, (
        "Army rules must not be empty."
    )

    for army_rule in army_rules.values():

        metrics = calculate_army_rule_metrics(
            army_rule,
        )

        assert metrics is not None, (
            f"Army rule '{army_rule.id}' metrics "
            "could not be calculated."
        )

        count = len(army_rules)

    label = (
        "army rule"
        if count == 1
        else "army rules"
    )

    print()
    print("========== ARMY RULE METRICS ==========")
    print(
        f"✓ Metrics calculated for {count} {label}"
    )

    if verbose:
        _print_army_rule_metrics(
            army_rules,
        )


# =====================================
# Verbose output
# =====================================

def _print_army_rule_metrics(
    army_rules,
) -> None:

    print()

    for army_rule in army_rules.values():

        metrics = calculate_army_rule_metrics(
            army_rule,
        )

        print(army_rule.name)
        print(metrics)