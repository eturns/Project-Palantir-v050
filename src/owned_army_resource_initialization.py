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
        profile = (
            fielded_model
            .configured_profile
            .profile
        )

        owned_states.append(
            OwnedHeroResourceState(
                owner=ResourceOwner(
                    fielded_model_id=fielded_model.id,
                ),
                resources=HeroResourceState(
                    remaining_might=profile.might,
                    remaining_will=profile.will,
                    remaining_fate=profile.fate,
                ),
            )
        )

    return tuple(owned_states)