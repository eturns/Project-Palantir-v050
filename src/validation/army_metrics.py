# =====================================
# Imports
# =====================================

from math import isfinite

from army_metric_densities import (
    calculate_army_metric_densities,
)
from army_metrics import (
    calculate_army_metrics,
)
from metric_constants import (
    METRIC_LABELS,
    METRIC_NAMES,
)
from army_rule_metric_calculator import (
    calculate_army_rule_metrics,
)
from profile_metrics import (
    calculate_profile_metrics,
)


# =====================================
# Validation
# =====================================

def validate_army_metrics(
    army,
    army_list,
    verbose: bool = False,
) -> None:
    """
    Validate army analysis metrics, raw army metrics,
    and metric densities.
    """

    analysis_metrics = army.analysis_metrics()

    # -------------------------------------
    # Army composition
    # -------------------------------------

    assert analysis_metrics.model_count > 0, (
        "Army model count must be greater than zero."
    )

    assert analysis_metrics.profile_density >= 0, (
        "Profile density cannot be negative."
    )

    assert analysis_metrics.model_density >= 0, (
        "Model density cannot be negative."
    )

    # -------------------------------------
    # Heroic resources
    # -------------------------------------

    assert analysis_metrics.might_density >= 0, (
        "Might density cannot be negative."
    )

    assert analysis_metrics.will_density >= 0, (
        "Will density cannot be negative."
    )

    assert analysis_metrics.fate_density >= 0, (
        "Fate density cannot be negative."
    )

    # -------------------------------------
    # Mobility
    # -------------------------------------

    assert analysis_metrics.average_movement >= 0, (
        "Average movement cannot be negative."
    )

    assert analysis_metrics.fast_model_density >= 0, (
        "Fast model density cannot be negative."
    )

    assert analysis_metrics.standard_model_density >= 0, (
        "Standard model density cannot be negative."
    )

    assert analysis_metrics.slow_model_density >= 0, (
        "Slow model density cannot be negative."
    )

    # -------------------------------------
    # Offensive potential
    # -------------------------------------

    assert analysis_metrics.average_fight >= 0, (
        "Average Fight cannot be negative."
    )

    assert analysis_metrics.average_strength >= 0, (
        "Average Strength cannot be negative."
    )

    assert analysis_metrics.average_attacks >= 0, (
        "Average Attacks cannot be negative."
    )

    assert analysis_metrics.high_fight_density >= 0, (
        "High Fight density cannot be negative."
    )

    assert analysis_metrics.high_strength_density >= 0, (
        "High Strength density cannot be negative."
    )

    # -------------------------------------
    # Defensive potential
    # -------------------------------------

    assert analysis_metrics.average_defence >= 0, (
        "Average Defence cannot be negative."
    )

    assert analysis_metrics.average_wounds >= 0, (
        "Average Wounds cannot be negative."
    )

    assert analysis_metrics.high_defence_density >= 0, (
        "High Defence density cannot be negative."
    )

    assert analysis_metrics.multi_wound_density >= 0, (
        "Multi-wound density cannot be negative."
    )

    # -------------------------------------
    # Generic army metrics
    # -------------------------------------

    army_metrics = calculate_army_metrics(
        army,
        army_list
    )

    expected_metrics = _calculate_expected_army_metrics(
        army,
        army_list,
    )

    metric_densities = calculate_army_metric_densities(
        army,
        army_list,
    )

    for metric_name in METRIC_NAMES:

        assert hasattr(army_metrics, metric_name), (
            f"Army metrics are missing '{metric_name}'."
        )

        assert hasattr(metric_densities, metric_name), (
            f"Army metric densities are missing "
            f"'{metric_name}'."
        )

        metric_value = getattr(
            army_metrics,
            metric_name,
        )  

        density_value = getattr(
            metric_densities,
            metric_name,
        )

        expected_value = expected_metrics[
            metric_name
        ]

        assert abs(
            metric_value - expected_value
        ) < 1e-9, (
            f"Army metric '{metric_name}' was aggregated "
            f"incorrectly. Expected {expected_value}, "
            f"received {metric_value}."
        )

        density_value = getattr(
            metric_densities,
            metric_name,
        )

        assert isinstance(metric_value, (int, float)), (
            f"Army metric '{metric_name}' must be numeric."
        )

        assert isinstance(density_value, (int, float)), (
            f"Army metric density '{metric_name}' "
            f"must be numeric."
        )

        assert isfinite(metric_value), (
            f"Army metric '{metric_name}' must be finite."
        )

        assert isfinite(density_value), (
            f"Army metric density '{metric_name}' "
            f"must be finite."
        )

        assert metric_value >= 0, (
            f"Army metric '{metric_name}' cannot be negative."
        )

        assert density_value >= 0, (
            f"Army metric density '{metric_name}' "
            f"cannot be negative."
        )

    print()
    print("========== ARMY METRICS ==========")
    print("✓ Army metrics calculated successfully")

    if verbose:
        _print_army_metrics(
            analysis_metrics,
            army_metrics,
            metric_densities,
            army_list,
        )

        _print_aggregation_audit(
            army,
            army_list,
        )


# =====================================
# Verbose output
# =====================================

def _print_army_metrics(
    analysis_metrics,
    army_metrics,
    metric_densities,
    army_list,
) -> None:

    print()
    print("Heroic Resources")
    print("----------------")
    print(
        f"Might Density   : "
        f"{analysis_metrics.might_density:.2f}"
    )
    print(
        f"Will Density    : "
        f"{analysis_metrics.will_density:.2f}"
    )
    print(
        f"Fate Density    : "
        f"{analysis_metrics.fate_density:.2f}"
    )

    print()
    print("Army Composition")
    print("----------------")
    print(
        f"Model Count     : "
        f"{analysis_metrics.model_count}"
    )
    print(
        f"Profile Density : "
        f"{analysis_metrics.profile_density:.2f}"
    )
    print(
        f"Model Density   : "
        f"{analysis_metrics.model_density:.2f}"
    )

    print()
    print("Mobility")
    print("--------")
    print(
        f"Average Movement       : "
        f"{analysis_metrics.average_movement:.2f}"
    )
    print(
        f"Fast Model Density     : "
        f"{analysis_metrics.fast_model_density:.2f}"
    )
    print(
        f"Standard Model Density : "
        f"{analysis_metrics.standard_model_density:.2f}"
    )
    print(
        f"Slow Model Density     : "
        f"{analysis_metrics.slow_model_density:.2f}"
    )

    print()
    print("Offensive Potential")
    print("-------------------")
    print(
        f"Average Fight         : "
        f"{analysis_metrics.average_fight:.2f}"
    )
    print(
        f"Average Strength      : "
        f"{analysis_metrics.average_strength:.2f}"
    )
    print(
        f"Average Attacks       : "
        f"{analysis_metrics.average_attacks:.2f}"
    )
    print(
        f"High Fight Density    : "
        f"{analysis_metrics.high_fight_density:.2f}"
    )
    print(
        f"High Strength Density : "
        f"{analysis_metrics.high_strength_density:.2f}"
    )

    print()
    print("Defensive Potential")
    print("-------------------")
    print(
        f"Average Defence      : "
        f"{analysis_metrics.average_defence:.2f}"
    )
    print(
        f"Average Wounds       : "
        f"{analysis_metrics.average_wounds:.2f}"
    )
    print(
        f"High Defence Density : "
        f"{analysis_metrics.high_defence_density:.2f}"
    )
    print(
        f"Multi-Wound Density  : "
        f"{analysis_metrics.multi_wound_density:.2f}"
    )

    print()
    print("Generic Army Metrics")
    print("--------------------")

    for metric_name in METRIC_NAMES:
        print(
            f"{METRIC_LABELS[metric_name]:14}: "
            f"{getattr(army_metrics, metric_name)}"
        )

    print()
    print("Army Metric Densities")
    print("---------------------")

    for metric_name in METRIC_NAMES:
        print(
            f"{METRIC_LABELS[metric_name]:14}: "
            f"{getattr(metric_densities, metric_name):.2f}"
        )

    print()
    print("Army Rule Metric Contributions")
    print("------------------------------")

    for army_rule in army_list.army_rules:

        print()
        print(army_rule.name)

        print("Raw tags:")

        for assignment in army_rule.ability_tags:
            print(
                f" - {assignment.tag.id}: "
                f"{assignment.weight}"
            )

        rule_metrics = calculate_army_rule_metrics(
            army_rule,
        )

        print("Metric contributions:")

        for metric in METRIC_NAMES:
            value = getattr(
                rule_metrics,
                metric,
            )

            if value != 0:
                print(
                    f" - {metric}: {value}"
                )

def _calculate_expected_army_metrics(
    army,
    army_list,
) -> dict[str, float]:
    """
    Independently reconstructs expected army metric totals.

    Profile contributions scale by entry quantity.
    Army-rule contributions are added once per rule.
    """

    expected = {
        metric_name: 0.0
        for metric_name in METRIC_NAMES
    }

    # Profile contributions
    for entry in army.entries:

        profile_metrics = calculate_profile_metrics(
            entry.profile,
        )

        for metric_name in METRIC_NAMES:
            expected[metric_name] += (
                getattr(
                    profile_metrics,
                    metric_name,
                )
                * entry.quantity
            )

    # Army-rule contributions
    for army_rule in army_list.army_rules:

        rule_metrics = calculate_army_rule_metrics(
            army_rule,
        )

        for metric_name in METRIC_NAMES:
            expected[metric_name] += getattr(
                rule_metrics,
                metric_name,
            )

    return expected

def _print_aggregation_audit(
    army,
    army_list,
) -> None:
    """
    Displays how profile quantities and army rules
    contribute to the final army metrics.
    """

    print()
    print("Army Metric Aggregation Audit")
    print("-----------------------------")

    print()
    print("Profile Contributions")
    print("---------------------")

    for entry in army.entries:

        profile_metrics = calculate_profile_metrics(
            entry.profile,
        )

        print()
        print(
            f"{entry.profile.name} "
            f"× {entry.quantity}"
        )

        has_contribution = False

        for metric_name in METRIC_NAMES:

            per_profile_value = getattr(
                profile_metrics,
                metric_name,
            )

            total_value = (
                per_profile_value
                * entry.quantity
            )

            if total_value == 0:
                continue

            has_contribution = True

            print(
                f" - {METRIC_LABELS[metric_name]}: "
                f"{per_profile_value} "
                f"× {entry.quantity} "
                f"= {total_value}"
            )

        if not has_contribution:
            print(" - No metric contribution")

    print()
    print("Army Rule Contributions")
    print("-----------------------")

    for army_rule in army_list.army_rules:

        rule_metrics = calculate_army_rule_metrics(
            army_rule,
        )

        print()
        print(
            f"{army_rule.name} × 1"
        )

        has_contribution = False

        for metric_name in METRIC_NAMES:

            value = getattr(
                rule_metrics,
                metric_name,
            )

            if value == 0:
                continue

            has_contribution = True

            print(
                f" - {METRIC_LABELS[metric_name]}: "
                f"{value}"
            )

        if not has_contribution:
            print(" - No metric contribution")