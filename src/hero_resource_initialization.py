from configured_profile import ConfiguredProfile
from hero_resource_state import HeroResourceState


def get_initial_hero_resource_state(
    configured_profile: ConfiguredProfile,
) -> HeroResourceState:
    return HeroResourceState(
        remaining_might=configured_profile.profile.might,
        remaining_will=configured_profile.profile.will,
        remaining_fate=configured_profile.profile.fate,
    )