"""Project Palantir army analysis service.

DEV-077S-I2-C-H3-B:
Expose mechanical Defence diagnostics without changing
existing metric assessments or battlefield ratings.
"""

from army_metric_densities import (
    calculate_army_metric_densities,
)
from army_metric_assessment import (
    assess_army_metrics,
)
from battlefield_assessment import (
    assess_battlefield,
)
from army_shooting_capability import (
    calculate_army_shooting_output_density,
)
from objective_normalisation import (
    normalise_shooting_output_density,
)
from projection_capability import (
    build_shooting_benchmark_defender,
)
from army_offence_capability import (
    calculate_army_offensive_output_density,
)
from mechanical_defence_diagnostics import (
    calculate_mechanical_defence_diagnostics,
)


def analyse_imported_army(
    army,
    army_list,
    points_limit: int,
    metric_thresholds,
) -> dict:
    """Run the complete army analysis pipeline.

    Mechanical Defence is returned as a diagnostic only.
    Existing metric assessment and battlefield logic
    remain unchanged.
    """

    validation_errors = army.validate(
        points_limit,
    )

    metrics = army.analysis_metrics()

    metric_densities = calculate_army_metric_densities(
        army,
        army_list,
    )

    offence_score = calculate_army_offensive_output_density(
        army,
    )

    shooting_density = calculate_army_shooting_output_density(
        army=army,
        defender=build_shooting_benchmark_defender(),
    )

    shooting_score = normalise_shooting_output_density(
        shooting_density,
    )

    # Independent diagnostic calculation.
    # Do not feed these values into the existing assessment
    # or scenario rating pipelines at this stage.
    mechanical_defence = (
        calculate_mechanical_defence_diagnostics(
            army,
        )
    )

    metric_assessments = assess_army_metrics(
        metric_densities,
        metric_thresholds,
        offence_value=offence_score,
        shooting_value=shooting_score,
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
        "mechanical_defence": mechanical_defence,
    }
