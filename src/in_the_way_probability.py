from fractions import Fraction


def get_in_the_way_success_probability(
    *,
    required_roll: int,
    modifier: int = 0,
) -> Fraction:
    if not 2 <= required_roll <= 6:
        raise ValueError(
            "required_roll must be between 2 and 6."
        )

    effective_required_roll = (
        required_roll - modifier
    )

    if effective_required_roll <= 1:
        return Fraction(1, 1)

    if effective_required_roll > 6:
        return Fraction(0, 1)

    return Fraction(
        7 - effective_required_roll,
        6,
    )