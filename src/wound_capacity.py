def calculate_wound_capacity(
    wounds: int,
) -> float:
    if (
        not isinstance(wounds, int)
        or isinstance(wounds, bool)
    ):
        raise TypeError(
            "wounds must be an int."
        )

    if wounds < 1:
        raise ValueError(
            "wounds must be at least 1."
        )

    return min(
        wounds / 4,
        1.0,
    )