MIGHT_DENSITY_MAX = 1.5
WILL_DENSITY_MAX = 2.0
FATE_DENSITY_MAX = 1.0


def _calculate_density(
    resource: int,
    army_points: int,
) -> float:
    if army_points <= 0:
        return 0.0

    return (
        resource
        / army_points
        * 100
    )


def _normalise_density(
    density: float,
    maximum: float,
) -> float:
    if maximum <= 0:
        return 0.0

    return min(
        max(
            density / maximum,
            0.0,
        ),
        1.0,
    )


def calculate_resource_capacity_score(
    might: int,
    will: int,
    fate: int,
    army_points: int,
) -> float:
    might_density = _calculate_density(
        might,
        army_points,
    )

    will_density = _calculate_density(
        will,
        army_points,
    )

    fate_density = _calculate_density(
        fate,
        army_points,
    )

    might_capacity = _normalise_density(
        might_density,
        MIGHT_DENSITY_MAX,
    )

    will_capacity = _normalise_density(
        will_density,
        WILL_DENSITY_MAX,
    )

    fate_capacity = _normalise_density(
        fate_density,
        FATE_DENSITY_MAX,
    )

    return (
        might_capacity
        + will_capacity
        + fate_capacity
    ) / 3