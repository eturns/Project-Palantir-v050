import pytest

from bound_in_shadow import (
    bound_in_shadow_auto_passes_courage,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule


def make_profile() -> Profile:
    return Profile(
        id="CASTELLAN_TEST",
        name="Castellan Test",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=5,
        defence=6,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="7+",
        might=0,
        will=10,
        fate=0,
        max_in_army=0,
    )


def add_bound_in_shadow(
    profile: Profile,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="BOUND_IN_SHADOW",
                name="Bound in Shadow",
                category=RuleCategory.SPECIAL,
            ),
        )
    )


def test_bound_in_shadow_passes_within_six_of_sauron():
    profile = make_profile()
    add_bound_in_shadow(profile)

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert bound_in_shadow_auto_passes_courage(
        configured,
        distance_to_sauron_inches=6,
    ) is True


def test_bound_in_shadow_passes_within_six_of_ringwraith():
    profile = make_profile()
    add_bound_in_shadow(profile)

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert bound_in_shadow_auto_passes_courage(
        configured,
        distance_to_friendly_ringwraith_inches=4,
    ) is True


def test_bound_in_shadow_does_not_apply_outside_six():
    profile = make_profile()
    add_bound_in_shadow(profile)

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert bound_in_shadow_auto_passes_courage(
        configured,
        distance_to_sauron_inches=6.1,
        distance_to_friendly_ringwraith_inches=8,
    ) is False


def test_non_bound_in_shadow_profile_does_not_auto_pass():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    assert bound_in_shadow_auto_passes_courage(
        configured,
        distance_to_sauron_inches=1,
    ) is False


def test_bound_in_shadow_rejects_negative_distance():
    profile = make_profile()
    add_bound_in_shadow(profile)

    configured = ConfiguredProfile(
        profile=profile,
    )

    with pytest.raises(
        ValueError,
        match="Distance cannot be negative",
    ):
        bound_in_shadow_auto_passes_courage(
            configured,
            distance_to_sauron_inches=-1,
        )