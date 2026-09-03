from army import Army
from profile_classification import (
    HeroicStatus,
)
from profiles import Profile
from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
)

def get_fog_of_war_preservation_profiles(
    *,
    army: Army,
    leader_profile: Profile,
) -> tuple[Profile, ...]:
    eligible_profiles = []

    for entry in army.entries:
        profile = entry.profile

        if profile is leader_profile:
            continue

        if profile.heroic_status is not HeroicStatus.HERO:
            continue

        eligible_profiles.append(profile)

    return tuple(eligible_profiles)

def select_fog_of_war_preservation_profile(
    *,
    army: Army,
    leader_profile: Profile,
    combat_benchmark,
    benchmark_fate: int | float,
) -> Profile | None:
    eligible_profiles = (
        get_fog_of_war_preservation_profiles(
            army=army,
            leader_profile=leader_profile,
        )
    )

    if not eligible_profiles:
        return None

    return max(
        eligible_profiles,
        key=lambda profile: (
            calculate_key_model_preservation_from_profile(
                profile=profile,
                benchmark=combat_benchmark,
                benchmark_fate=benchmark_fate,
            ).value
        ),
    )