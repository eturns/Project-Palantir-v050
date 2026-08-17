"""
Project Palantír
================

File:
    army_metrics.py

Purpose:
    Represents the calculated battlefield metrics for an Army.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-020 – Army Metrics
"""

# ============================================================================
# Imports
# ============================================================================

from army import Army
from army_metrics_entity import ArmyMetrics
from profile_metrics import calculate_profile_metrics
from metric_constants import METRIC_NAMES
from army_list import ArmyList
from army_rule_metric_calculator import (
    calculate_army_rule_metrics,
)
from army_analysis_context_builder import (
    build_army_analysis_context,
)
from repeated_ability_scaling import (
    count_models_with_special_rule,
    count_models_with_parameterised_special_rule,
    diminishing_returns_multiplier,
    highest_special_rule_parameter,
)


# ============================================================================
# Functions
# ============================================================================
def _add_repeated_ability_metrics(
    army_metrics: ArmyMetrics,
    army: Army,
) -> None:
    """
    Adds army-level contributions from repeated abilities.
    """

    terror_count = count_models_with_special_rule(
        army,
        "TERROR",
    )

    terror_multiplier = diminishing_returns_multiplier(
        terror_count,
    )

    army_metrics.courage += (
        1.5
        * terror_multiplier
    )

    army_metrics.control += (
        1.0
        * terror_multiplier
    )

    harbinger_range = highest_special_rule_parameter(
        army,
        "HARBINGER_OF_EVIL",
    )

    harbinger_count = (
        count_models_with_parameterised_special_rule(
            army,
            "HARBINGER_OF_EVIL",
        )
    )

    if (
        harbinger_range is not None
        and harbinger_count > 0
    ):
        range_multiplier = (
            harbinger_range / 12
        ) ** 0.5

        coverage_multiplier = (
            diminishing_returns_multiplier(
                harbinger_count,
            )
        )

        army_metrics.courage += (
            1.0
            * range_multiplier
            * coverage_multiplier
        )

    spider_webs_count = count_models_with_special_rule(
        army,
        "SPIDER_WEBS",
    )

    spider_webs_multiplier = diminishing_returns_multiplier(
        spider_webs_count,
    )

    army_metrics.control += (
        1.75
        * spider_webs_multiplier
    )

    slayer_of_men_count = count_models_with_special_rule(
        army,
        "ANGMAR_ARISE_SOM",
    )

    if slayer_of_men_count >= 2:
        army_metrics.offence += 0.5

def calculate_army_metrics(
    army: Army,
    army_list: ArmyList,
) -> ArmyMetrics:
    """
    Calculates the battlefield metrics for an Army.
    """

    army_metrics = ArmyMetrics()

    _add_repeated_ability_metrics(
        army_metrics,
        army,
    )
    
    context = build_army_analysis_context(
        army,
        army_list,
    )
    
    for entry in army.entries:

        profile_metrics = calculate_profile_metrics(
            entry.profile,
            context,
        )

        for metric in METRIC_NAMES:

            setattr(
                army_metrics,
                metric,
                getattr(
                    army_metrics,
                    metric,
                )
                + (
                    getattr(
                        profile_metrics,
                        metric,
                    )
                    * entry.quantity
                ),
            )
      
    for army_rule in army_list.army_rules:

        army_rule_metrics = calculate_army_rule_metrics(
            army_rule,
        )

        for metric in METRIC_NAMES:

            setattr(
                army_metrics,
                metric,
                getattr(
                    army_metrics,
                    metric,
                )
                + getattr(
                    army_rule_metrics,
                    metric,
                ),
            )

    return army_metrics