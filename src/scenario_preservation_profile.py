from army import Army
from fielded_model import FieldedModel
from profile_classification import (
    HeroicStatus,
)
from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
)


def get_fog_of_war_preservation_models(
    *,
    army: Army,
    leader_model: FieldedModel,
) -> tuple[FieldedModel, ...]:
    eligible_models = []

    for fielded_model in army.fielded_models():
        if fielded_model.id == leader_model.id:
            continue

        profile = (
            fielded_model
            .configured_profile
            .profile
        )

        if profile.heroic_status is not HeroicStatus.HERO:
            continue

        eligible_models.append(
            fielded_model
        )

    return tuple(eligible_models)


def select_fog_of_war_preservation_model(
    *,
    army: Army,
    leader_model: FieldedModel,
    combat_benchmark,
    benchmark_fate: int | float,
) -> FieldedModel | None:
    eligible_models = (
        get_fog_of_war_preservation_models(
            army=army,
            leader_model=leader_model,
        )
    )

    if not eligible_models:
        return None

    return max(
        eligible_models,
        key=lambda fielded_model: (
            calculate_key_model_preservation_from_profile(
                profile=(
                    fielded_model
                    .configured_profile
                    .profile
                ),
                benchmark=combat_benchmark,
                benchmark_fate=benchmark_fate,
            ).value
        ),
    )