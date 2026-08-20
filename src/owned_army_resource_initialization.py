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

    for entry in sorted(
        army.entries,
        key=lambda army_entry: army_entry.profile.id,
    ):
        for instance_index in range(
            1,
            entry.quantity + 1,
        ):
            owned_states.append(
                OwnedHeroResourceState(
                    owner=ResourceOwner(
                        profile_id=entry.profile.id,
                        instance_index=instance_index,
                    ),
                    resources=HeroResourceState(
                        remaining_might=entry.profile.might,
                        remaining_will=entry.profile.will,
                        remaining_fate=entry.profile.fate,
                    ),
                )
            )

    return tuple(owned_states)