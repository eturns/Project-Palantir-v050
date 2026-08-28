from fractions import Fraction


def calculate_expected_resurrection_bonus(
    resurrection_capable_models: int,
    starting_models: int,
    success_probability: int | float | Fraction,
) -> float:
    if (
        not isinstance(resurrection_capable_models, int)
        or isinstance(resurrection_capable_models, bool)
    ):
        raise TypeError(
            "resurrection_capable_models must be an int."
        )

    if (
        not isinstance(starting_models, int)
        or isinstance(starting_models, bool)
    ):
        raise TypeError(
            "starting_models must be an int."
        )

    if resurrection_capable_models < 0:
        raise ValueError(
            "resurrection_capable_models cannot be negative."
        )

    if starting_models <= 0:
        raise ValueError(
            "starting_models must be greater than zero."
        )

    if resurrection_capable_models > starting_models:
        raise ValueError(
            "resurrection_capable_models cannot exceed starting_models."
        )

    if (
        not isinstance(
            success_probability,
            (int, float, Fraction),
        )
        or isinstance(success_probability, bool)
    ):
        raise TypeError(
            "success_probability must be numeric."
        )

    if not 0 <= success_probability <= 1:
        raise ValueError(
            "success_probability must be between 0 and 1."
        )

    resurrection_model_fraction = (
        resurrection_capable_models
        / starting_models
    )

    return float(
        resurrection_model_fraction
        * success_probability
    )