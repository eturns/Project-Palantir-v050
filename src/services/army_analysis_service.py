"""Project Palantir army analysis service.

DEV-077S-I2-F4-A1: append diagnostic-only Magic alongside established
Defence, Mobility and Courage evidence; leave assessments unchanged.
"""
from army_metric_densities import calculate_army_metric_densities
from army_metric_assessment import assess_army_metrics
from battlefield_assessment import assess_battlefield
from army_shooting_capability import calculate_army_shooting_output_density
from objective_normalisation import normalise_shooting_output_density
from projection_capability import build_shooting_benchmark_defender
from army_offence_capability import calculate_army_offensive_output_density
from mechanical_defence_diagnostics import calculate_mechanical_defence_diagnostics
from mobility_integration_contract import build_mobility_integration_contract
from courage_integration_contract import build_courage_integration_contract
from mechanical_magic_army_contract import build_army_magic_contract
from mechanical_magic_completeness import audit_army_magic_completeness
from army import Army
from configured_profile import ConfiguredProfile


def analyse_imported_army(army, army_list, points_limit: int, metric_thresholds) -> dict:
    """Run existing analysis and append uncalibrated mechanical diagnostics."""
    validation_errors = army.validate(points_limit)
    metrics = army.analysis_metrics()
    metric_densities = calculate_army_metric_densities(army, army_list)
    offence_score = calculate_army_offensive_output_density(army)
    shooting_density = calculate_army_shooting_output_density(
        army=army, defender=build_shooting_benchmark_defender()
    )
    shooting_score = normalise_shooting_output_density(shooting_density)

    # Diagnostics are NEVER inputs to the ratings/scenario pipelines.
    mechanical_defence = calculate_mechanical_defence_diagnostics(army)
    mechanical_mobility = build_mobility_integration_contract(army)
    # Legacy doubles may not support mechanical contracts. Errors for genuine
    # Army objects must propagate: unavailable evidence is not a zero score.
    mechanical_courage = None
    mechanical_magic = None
    mechanical_magic_completeness = None
    if isinstance(army, Army):
        courage_benchmark = build_shooting_benchmark_defender()
        if isinstance(courage_benchmark, ConfiguredProfile):
            mechanical_courage = build_courage_integration_contract(
                army, courage_benchmark
            )
        mechanical_magic_completeness = audit_army_magic_completeness(army)
        if mechanical_magic_completeness.is_complete:
            mechanical_magic = build_army_magic_contract(army)

    metric_assessments = assess_army_metrics(
        metric_densities, metric_thresholds,
        offence_value=offence_score, shooting_value=shooting_score,
    )
    battlefield_assessments = assess_battlefield(metric_assessments)
    return {
        "validation_errors": validation_errors,
        "metrics": metrics,
        "metric_densities": metric_densities,
        "metric_assessments": metric_assessments,
        "battlefield_assessments": battlefield_assessments,
        "mechanical_defence": mechanical_defence,
        "mechanical_mobility": mechanical_mobility,
        "mechanical_courage": mechanical_courage,
        "mechanical_magic": mechanical_magic,
        "mechanical_magic_completeness": mechanical_magic_completeness,
    }
