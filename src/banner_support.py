from configured_profile import ConfiguredProfile


BANNER_WARGEAR_ID = "WG_BANNER"
BANNER_RANGE_INCHES = 3.0


def carries_banner(
    profile: ConfiguredProfile,
) -> bool:
    return BANNER_WARGEAR_ID in {
        wargear.id
        for wargear in profile.effective_wargear
    }


def has_banner_support(
    banner_distances_inches: tuple[float, ...],
) -> bool:
    return any(
        distance <= BANNER_RANGE_INCHES
        for distance in banner_distances_inches
    )