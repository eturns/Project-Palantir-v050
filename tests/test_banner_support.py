from configured_profile import ConfiguredProfile
from profiles import Profile
from wargear import Wargear

from banner_support import (
    carries_banner,
    has_banner_support,
)


def make_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_profile_with_banner_is_recognised():
    profile = make_profile()

    profile.default_wargear.append(
        Wargear(
            id="WG_BANNER",
            name="Banner",
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert carries_banner(configured) is True


def test_profile_without_banner_is_not_recognised():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    assert carries_banner(configured) is False


def test_banner_within_three_inches_provides_support():
    assert has_banner_support(
        (2.5,),
    ) is True


def test_banner_exactly_three_inches_provides_support():
    assert has_banner_support(
        (3.0,),
    ) is True


def test_banner_over_three_inches_does_not_provide_support():
    assert has_banner_support(
        (3.1,),
    ) is False


def test_any_one_of_multiple_banners_can_provide_support():
    assert has_banner_support(
        (5.0, 2.8, 6.0),
    ) is True


def test_multiple_nearby_banners_still_only_mean_support_available():
    assert has_banner_support(
        (1.0, 2.0, 3.0),
    ) is True


def test_no_banners_means_no_support():
    assert has_banner_support(
        (),
    ) is False