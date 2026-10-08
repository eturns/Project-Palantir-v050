from fractions import Fraction
from configured_profile import ConfiguredProfile

def parse_shoot_value(
    shoot_value: str,
) -> int:
    """
    Parses an MESBG Shoot characteristic such as "4+"
    into its required D6 roll.
    """

    if not isinstance(shoot_value, str):
        raise ValueError(
            "Shoot value must use MESBG target notation."
        )

    if not shoot_value.endswith("+"):
        raise ValueError(
            "Shoot value must use MESBG target notation."
        )

    target_text = shoot_value[:-1]

    if not target_text.isdigit():
        raise ValueError(
            "Shoot value must use MESBG target notation."
        )

    target = int(target_text)

    if not 2 <= target <= 6:
        raise ValueError(
            "Shoot value must be between 2+ and 6+."
        )

    return target


def get_shooting_hit_probability(
    shoot_value: str,
    *,
    modifier: int = 0,
) -> Fraction:
    """
    Returns the probability of hitting with one standard
    shooting attack after applying a To Hit modifier.

    Positive modifiers improve the roll.
    Negative modifiers worsen it.
    """

    required_roll = parse_shoot_value(
        shoot_value,
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

def get_shooting_hit_probability_for_profile(
    profile: ConfiguredProfile,
    *,
    modifier: int = 0,
) -> Fraction:
    """
    Returns the shooting hit probability for a configured
    Profile using its effective Shoot value and supplied
    To Hit modifier.
    """

    return get_shooting_hit_probability(
        profile.effective_shooting,
        modifier=modifier,
    )