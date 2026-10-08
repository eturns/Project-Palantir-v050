"""DEV-077S-I2-C-G7-C1.

Integration tests for Necromancer-supported resurrection
in the mechanical Defence capability calculation.
"""

import pytest

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule


def create_nazgul() -> ConfiguredProfile:
    profile = Profile(
        id="TEST_DG_NAZGUL",
        name="Test Dol Guldur Nazgul",
        points=80,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="UNHOLY_RESURRECTION",
                name="Unholy Resurrection",
                category=RuleCategory.SPECIAL,
            ),
            parameter=None,
        )
    )

    return ConfiguredProfile(profile=profile)


def recovery_score(
    *,
    necromancer_will=None,
    distance=None,
    will_to_spend=0,
):
    return calculate_profile_defensive_combat_score(
        create_nazgul(),
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
        include_resurrection=True,
        necromancer_remaining_will=necromancer_will,
        distance_inches=distance,
        will_points_available_to_spend=will_to_spend,
    )


def test_unsupported_nazgul_uses_standard_resurrection():
    result = recovery_score()

    combat_survival = (
        calculate_profile_defensive_combat_score(
            create_nazgul(),
            DEFAULT_COMBAT_BENCHMARK,
            engagements=3,
        )
    )

    expected = (
        combat_survival
        + (1 - combat_survival) * (2 / 3)
    )

    assert result == pytest.approx(expected)


def test_necromancer_support_improves_recovery():
    unsupported = recovery_score()

    supported = recovery_score(
        necromancer_will=20,
        distance=18,
    )

    assert supported > unsupported


def test_outside_range_has_no_support_bonus():
    unsupported = recovery_score()

    outside_range = recovery_score(
        necromancer_will=20,
        distance=18.1,
    )

    assert outside_range == pytest.approx(unsupported)


def test_necromancer_range_changes_with_will():
    supported_at_twenty = recovery_score(
        necromancer_will=20,
        distance=15,
    )

    unsupported_at_nineteen = recovery_score(
        necromancer_will=19,
        distance=15,
    )

    assert (
        supported_at_twenty
        > unsupported_at_nineteen
    )


def test_explicit_will_spend_improves_resurrection():
    supported = recovery_score(
        necromancer_will=20,
        distance=18,
        will_to_spend=0,
    )

    boosted = recovery_score(
        necromancer_will=20,
        distance=18,
        will_to_spend=1,
    )

    assert boosted > supported
    assert boosted == pytest.approx(1.0)


def test_will_spend_cannot_exceed_remaining_will():
    with pytest.raises(
        ValueError,
        match="Cannot spend more Will",
    ):
        recovery_score(
            necromancer_will=1,
            distance=6,
            will_to_spend=2,
        )


def test_support_requires_both_context_inputs():
    with pytest.raises(ValueError):
        recovery_score(
            necromancer_will=20,
        )

    with pytest.raises(ValueError):
        recovery_score(
            distance=6,
        )


def test_spending_will_requires_support_context():
    with pytest.raises(ValueError):
        recovery_score(
            will_to_spend=1,
        )
