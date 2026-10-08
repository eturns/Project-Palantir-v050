from army_metric_densities import (
    calculate_army_metric_densities,
)
from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)
from objective_normalisation import (
    COMMAND_EFFECT_DENSITY_MAX,
    COURAGE_EFFECT_DENSITY_MAX,
    DEFENCE_EFFECT_DENSITY_MAX,
    HERO_HUNTING_EFFECT_DENSITY_MAX,
    OFFENCE_EFFECT_DENSITY_MAX,
    SHOOTING_EFFECT_DENSITY_MAX,
    normalise_battlefield_effect,
    normalise_shooting_output_density,
)


def build_battlefield_effects_inputs(
    army,
    army_list,
    *,
    shooting_density: float | None = None,
) -> BattlefieldEffectsInputs:
    densities = calculate_army_metric_densities(
        army,
        army_list,
    )

    if shooting_density is None:
        shooting_score = normalise_battlefield_effect(
            densities.shooting,
            SHOOTING_EFFECT_DENSITY_MAX,
        )
    else:
        shooting_score = normalise_shooting_output_density(
            shooting_density,
        )

    return BattlefieldEffectsInputs(
        offence=normalise_battlefield_effect(
            densities.offence,
            OFFENCE_EFFECT_DENSITY_MAX,
        ),
        defence=normalise_battlefield_effect(
            densities.defence,
            DEFENCE_EFFECT_DENSITY_MAX,
        ),
        shooting=shooting_score,
        courage=normalise_battlefield_effect(
            densities.courage,
            COURAGE_EFFECT_DENSITY_MAX,
        ),
        command=normalise_battlefield_effect(
            densities.command,
            COMMAND_EFFECT_DENSITY_MAX,
        ),
        hero_hunting=normalise_battlefield_effect(
            densities.hero_hunting,
            HERO_HUNTING_EFFECT_DENSITY_MAX,
        ),
    )