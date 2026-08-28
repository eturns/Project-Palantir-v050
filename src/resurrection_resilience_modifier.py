def calculate_resurrection_resilience_modifier(
    expected_resurrection_bonus: int | float,
    resilience_weight: int | float,
) -> float:
    inputs = (
        expected_resurrection_bonus,
        resilience_weight,
    )

    if any(
        (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        )
        for value in inputs
    ):
        raise TypeError(
            "resurrection resilience inputs must be int or float."
        )

    if not 0.0 <= expected_resurrection_bonus <= 1.0:
        raise ValueError(
            "expected_resurrection_bonus must be between 0.0 and 1.0."
        )

    if not 0.0 <= resilience_weight <= 1.0:
        raise ValueError(
            "resilience_weight must be between 0.0 and 1.0."
        )

    return (
        expected_resurrection_bonus
        * resilience_weight
    )