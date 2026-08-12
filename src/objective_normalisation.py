MODEL_PRESENCE_MAX_PER_100_POINTS = 10.0
MANOEUVRABILITY_MAX = 10.0
CONTROL_DENSITY_MAX = 5.0

# Provisional v1 calibration.
# Reassess during the planned REL-0.9 calibration run.
MAGIC_DENSITY_MAX = 3.0
OFFENCE_EFFECT_DENSITY_MAX = 4.0625
DEFENCE_EFFECT_DENSITY_MAX = 2.8125
SHOOTING_EFFECT_DENSITY_MAX = 3.125
COURAGE_EFFECT_DENSITY_MAX = 4.0625
COMMAND_EFFECT_DENSITY_MAX = 3.125
HERO_HUNTING_EFFECT_DENSITY_MAX = 3.125


def normalise_model_presence(
    model_count: int,
    army_points: int,
) -> float:
    if army_points <= 0:
        return 0.0

    models_per_100_points = (
        model_count
        * 100
        / army_points
    )

    return min(
        max(
            models_per_100_points
            / MODEL_PRESENCE_MAX_PER_100_POINTS,
            0.0,
        ),
        1.0,
    )


def normalise_manoeuvrability(
    manoeuvrability: float,
) -> float:
    return min(
        max(
            manoeuvrability
            / MANOEUVRABILITY_MAX,
            0.0,
        ),
        1.0,
    )


def normalise_control(
    control_density: float,
) -> float:
    return min(
        max(
            control_density
            / CONTROL_DENSITY_MAX,
            0.0,
        ),
        1.0,
    )


def normalise_magic(
    magic_density: float,
) -> float:
    return min(
        max(
            magic_density
            / MAGIC_DENSITY_MAX,
            0.0,
        ),
        1.0,
    )

def normalise_battlefield_effect(
    value: float,
    maximum: float,
) -> float:
    if maximum <= 0:
        raise ValueError(
            "Battlefield effect maximum must be greater than zero."
        )

    return min(
        max(
            value / maximum,
            0.0,
        ),
        1.0,
    )