from army import Army
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from resource_owner import ResourceOwner


def get_initial_owned_hero_resource_states(
    army: Army,
) -> tuple[OwnedHeroResourceState, ...]:
    owned_states: list[OwnedHeroResourceState] = []

    for fielded_model in army.fielded_models():
        if fielded_model.configured_profile is None:
            continue

        configured_profile = (
            fielded_model
            .configured_profile
        )

        owned_states.append(
            OwnedHeroResourceState(
                owner=ResourceOwner(
                    fielded_model_id=fielded_model.id,
                ),
                resources=HeroResourceState(
                    remaining_might=(
                        configured_profile.effective_might
                    ),
                    remaining_will=(
                        configured_profile.effective_will
                    ),
                    remaining_fate=(
                        configured_profile.effective_fate
                    ),
                ),
            )
        )

    return tuple(owned_states)