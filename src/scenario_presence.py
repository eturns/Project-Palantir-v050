from profiles import Profile

def calculate_scenario_presence_weight(
    dominant_value: int | None,
) -> int:
    if dominant_value is None:
        return 1

    if (
        not isinstance(dominant_value, int)
        or isinstance(dominant_value, bool)
    ):
        raise TypeError(
            "dominant_value must be an int or None."
        )

    if dominant_value < 1:
        raise ValueError(
            "dominant_value must be at least 1."
        )

    return dominant_value

def calculate_dominant_presence_weight(
    dominant_values: tuple[int, ...],
) -> int:
    for value in dominant_values:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "dominant_values must contain only ints."
            )

        if value < 1:
            raise ValueError(
                "dominant_values must contain values of at least 1."
            )

    if not dominant_values:
        return 1

    return max(dominant_values)

def calculate_total_scenario_presence(
    presence_weights: tuple[int, ...],
) -> int:
    for value in presence_weights:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "presence_weights must contain only ints."
            )

        if value < 1:
            raise ValueError(
                "presence_weights must contain values of at least 1."
            )

    return sum(presence_weights)

def calculate_model_scenario_presence(
    dominant_values: tuple[int, ...],
) -> int:
    return calculate_dominant_presence_weight(
        dominant_values=dominant_values,
    )

def calculate_total_model_scenario_presence(
    model_dominant_values: tuple[tuple[int, ...], ...],
) -> int:
    for dominant_values in model_dominant_values:
        if not isinstance(dominant_values, tuple):
            raise TypeError(
                "model_dominant_values must contain only tuples."
            )

    presence_weights = tuple(
        calculate_model_scenario_presence(
            dominant_values=dominant_values,
        )
        for dominant_values in model_dominant_values
    )

    return calculate_total_scenario_presence(
        presence_weights=presence_weights,
    )

def calculate_profile_scenario_presence(
    profile: Profile,
) -> int:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    dominant_values = tuple(
        assignment.parameter
        for assignment in profile.special_rules
        if (
            assignment.rule.id == "DOMINANT"
            and isinstance(assignment.parameter, int)
            and not isinstance(assignment.parameter, bool)
        )
    )

    return calculate_model_scenario_presence(
        dominant_values=dominant_values,
    )

def calculate_army_scenario_presence(
    profiles: tuple[Profile, ...],
) -> int:
    for profile in profiles:
        if not isinstance(profile, Profile):
            raise TypeError(
                "profiles must contain only Profile values."
            )

    return sum(
        calculate_profile_scenario_presence(
            profile=profile,
        )
        for profile in profiles
    )