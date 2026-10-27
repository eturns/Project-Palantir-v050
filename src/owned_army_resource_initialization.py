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

    # Preserve the same entry-index and instance identities as Army.fielded_models.
    by_entry_index = {i: entry for i, entry in enumerate(army.entries, 1)}
    for fielded_model in army.fielded_models():
        if fielded_model.configured_profile is None:
            continue

        configured_profile = (
            fielded_model
            .configured_profile
        )
        entry_index = int(fielded_model.id.rsplit(':', 2)[-2])
        entry = by_entry_index[entry_index]
        if entry.configured_profile is not configured_profile:
            raise ValueError('fielded resource identity mismatch')

        owned_states.append(
            OwnedHeroResourceState(
                owner=ResourceOwner(
                    fielded_model_id=fielded_model.id,
                ),
                resources=HeroResourceState(
                    remaining_might=(
                        getattr(entry, "starting_resource_overrides", {}).get(
                            "might", configured_profile.effective_might
                        )
                    ),
                    remaining_will=(
                        getattr(entry, "starting_resource_overrides", {}).get(
                            "will", configured_profile.effective_will
                        )
                    ),
                    remaining_fate=(
                        getattr(entry, "starting_resource_overrides", {}).get(
                            "fate", configured_profile.effective_fate
                        )
                    ),
                ),
            )
        )

    return tuple(owned_states)