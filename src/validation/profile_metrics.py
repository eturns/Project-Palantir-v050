from metric_constants import (
    METRIC_NAMES,
)

from profile_metrics import (
    calculate_profile_metrics,
)

from validation.output import (
    print_heading,
    print_pass,
)


def validate_profile_metrics(
    profiles_by_id,
    verbose: bool = False,
) -> None:
    """
    Validates profile metric calculations.
    """

    witch_king = profiles_by_id["DG_WK"]
    necromancer = profiles_by_id["DG_NEC"]

    witch_king_metrics = calculate_profile_metrics(
        witch_king,
    )

    necromancer_metrics = calculate_profile_metrics(
        necromancer,
    )

    print_heading(
        "PROFILE METRICS",
    )

    print_pass(
        "Profile metrics calculated successfully",
    )

    if not verbose:
        return

    _print_profile_metrics(
        witch_king,
        witch_king_metrics,
    )

    _print_profile_metrics(
        necromancer,
        necromancer_metrics,
    )


def _print_profile_metrics(
    profile,
    metrics,
) -> None:
    """
    Prints detailed profile metric output.
    """

    print()
    print(profile.name)
    print()

    for metric in METRIC_NAMES:
        print(
            f"{metric.replace('_', ' ').title():14}: "
            f"{getattr(metrics, metric)}"
        )