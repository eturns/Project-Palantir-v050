from fractions import Fraction


FATE_SUCCESS_TARGET = 4


def get_fate_success_probability(
    required_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if required_roll <= 1:
        return Fraction(1, 1)

    if required_roll > 6:
        return Fraction(0, 1)

    return Fraction(
        7 - required_roll,
        6,
    )

def get_fate_prevention_probability(
    fate_points: int,
    required_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if fate_points < 0:
        raise ValueError(
            "Fate points cannot be negative."
        )

    if fate_points == 0:
        return Fraction(0, 1)

    success_probability = get_fate_success_probability(
        required_roll=required_roll,
    )

    failure_probability = (
        Fraction(1, 1) - success_probability
    )

    return (
        Fraction(1, 1)
        - failure_probability ** fate_points
    )

def get_expected_fate_spent(
    fate_points: int,
    required_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if fate_points < 0:
        raise ValueError(
            "Fate points cannot be negative."
        )

    if fate_points == 0:
        return Fraction(0, 1)

    success_probability = get_fate_success_probability(
        required_roll=required_roll,
    )

    failure_probability = (
        Fraction(1, 1) - success_probability
    )

    expected_spent = Fraction(0, 1)

    for fate_index in range(fate_points):
        expected_spent += (
            failure_probability ** fate_index
        )

    return expected_spent

def get_fate_success_probability_with_might(
    might_points: int,
    required_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if might_points < 0:
        raise ValueError(
            "Might points cannot be negative."
        )

    successful_natural_rolls = 0

    for natural_roll in range(1, 7):
        might_required = max(
            0,
            required_roll - natural_roll,
        )

        if might_required <= might_points:
            successful_natural_rolls += 1

    return Fraction(
        successful_natural_rolls,
        6,
    )

def get_fate_prevention_probability_with_might(
    fate_points: int,
    might_points: int,
    required_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if fate_points < 0:
        raise ValueError(
            "Fate points cannot be negative."
        )

    if might_points < 0:
        raise ValueError(
            "Might points cannot be negative."
        )

    if fate_points == 0:
        return Fraction(0, 1)

    success_probability = (
        get_fate_success_probability_with_might(
            might_points=might_points,
            required_roll=required_roll,
        )
    )

    failure_probability = (
        Fraction(1, 1) - success_probability
    )

    return (
        Fraction(1, 1)
        - failure_probability ** fate_points
    )