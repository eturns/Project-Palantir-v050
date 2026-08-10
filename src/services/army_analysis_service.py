from army_metric_densities import (
    calculate_army_metric_densities,
)
from army_metric_assessment import (
    assess_army_metrics,
)
from battlefield_assessment import (
    assess_battlefield,
)

def analyse_imported_army(
    army,
    army_list,
    points_limit: int,
    metric_thresholds,
) -> dict:
    """
    Runs the complete Project Palantír analysis pipeline
    for an imported army.
    """

    validation_errors = army.validate(
        points_limit,
    )

    metrics = army.analysis_metrics()

    metric_densities = calculate_army_metric_densities(
        army,
        army_list,
    )

    metric_assessments = assess_army_metrics(
        metric_densities,
        metric_thresholds,
    )

    battlefield_assessments = assess_battlefield(
        metric_assessments,
    )

    return {
        "validation_errors": validation_errors,
        "metrics": metrics,
        "metric_densities": metric_densities,
        "metric_assessments": metric_assessments,
        "battlefield_assessments": battlefield_assessments,
    }