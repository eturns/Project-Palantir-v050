import pytest

from configured_profile import ConfiguredProfile
from profile_classification import (
    HeroicStatus,
    ModelType,
)
from profiles import Profile
from spider_webs import (
    SpiderWebsTargetState,
    resolve_spider_webs,
)


def make_profile(
    profile_id: str,
    *,
    heroic_status: HeroicStatus = HeroicStatus.WARRIOR,
    cavalry: bool = False,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        heroic_status=heroic_status,
        model_types={
            (
                ModelType.CAVALRY
                if cavalry
                else ModelType.INFANTRY
            ),
        },
    )


def test_spider_webs_hits_and_paralyses_target_within_eight_inches():
    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=8,
            hit_successful=True,
        ),
    )

    assert result.in_range is True
    assert result.target_paralysed is True
    assert result.rider_paralysed is True
    assert result.mount_paralysed is False


def test_spider_webs_has_no_effect_beyond_eight_inches():
    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=8.1,
            hit_successful=True,
        ),
    )

    assert result.in_range is False
    assert result.target_paralysed is False


def test_spider_webs_requires_successful_hit():
    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=6,
            hit_successful=False,
        ),
    )

    assert result.target_paralysed is False


def test_spider_webs_hits_both_rider_and_mount():
    target = ConfiguredProfile(
        profile=make_profile(
            "CAVALRY_TARGET",
            cavalry=True,
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=6,
            hit_successful=True,
        ),
    )

    assert result.rider_paralysed is True
    assert result.mount_paralysed is True


def test_hero_can_spend_one_fate_to_avoid_spider_webs():
    target = ConfiguredProfile(
        profile=make_profile(
            "HERO_TARGET",
            heroic_status=HeroicStatus.HERO,
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=6,
            hit_successful=True,
            fate_available=2,
            spend_fate_to_avoid=True,
        ),
    )

    assert result.fate_spent == 1
    assert result.target_paralysed is False


def test_hero_without_fate_cannot_avoid_spider_webs():
    target = ConfiguredProfile(
        profile=make_profile(
            "HERO_TARGET",
            heroic_status=HeroicStatus.HERO,
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=6,
            hit_successful=True,
            fate_available=0,
            spend_fate_to_avoid=True,
        ),
    )

    assert result.fate_spent == 0
    assert result.target_paralysed is True


def test_warrior_cannot_spend_fate_to_avoid_spider_webs():
    target = ConfiguredProfile(
        profile=make_profile(
            "WARRIOR_TARGET",
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=6,
            hit_successful=True,
            fate_available=1,
            spend_fate_to_avoid=True,
        ),
    )

    assert result.fate_spent == 0
    assert result.target_paralysed is True


def test_cavalry_hero_fate_negates_webs_for_rider_and_mount():
    target = ConfiguredProfile(
        profile=make_profile(
            "CAVALRY_HERO",
            heroic_status=HeroicStatus.HERO,
            cavalry=True,
        ),
    )

    result = resolve_spider_webs(
        target,
        state=SpiderWebsTargetState(
            distance_inches=6,
            hit_successful=True,
            fate_available=1,
            spend_fate_to_avoid=True,
        ),
    )

    assert result.fate_spent == 1
    assert result.rider_paralysed is False
    assert result.mount_paralysed is False


def test_spider_webs_rejects_negative_distance():
    with pytest.raises(ValueError):
        SpiderWebsTargetState(
            distance_inches=-1,
            hit_successful=True,
        )