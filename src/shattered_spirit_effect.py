from configured_profile import ConfiguredProfile
from shattered_spirit_state import (
    ShatteredSpiritState,
)


def get_shattered_spirit_attacks(
    configured_profile: ConfiguredProfile,
    state: ShatteredSpiritState | None,
) -> int:
    if (
        state is not None
        and state.is_empowered
    ):
        return 3

    return configured_profile.effective_attacks


def get_shattered_spirit_strength(
    configured_profile: ConfiguredProfile,
    state: ShatteredSpiritState | None,
) -> int:
    if (
        state is not None
        and state.is_empowered
    ):
        return 4

    return configured_profile.effective_strength