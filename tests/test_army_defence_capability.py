"""DEV-077S-I2-C-H1: Army Defence capability tests."""

import pytest

from army import Army
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profiles import Profile
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from database.rule_category import RuleCategory
from special_rule import SpecialRule

from army_defence_capability import (
    calculate_army_defensive_combat_score,
    calculate_army_defensive_output_density,
)


def create_profile(
    *,
    profile_id="TEST_DEFENDER",
    points=20,
    fight=4,
    defence=6,
    attacks=1,
    wounds=1,
    fate=0,
    resurrection=False,
):
    profile = Profile(
        id=profile_id,
        name=profile_id,
        points=points,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=4,
        defence=defence,
        attacks=attacks,
        wounds=wounds,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=fate,
        max_in_army=100,
    )

    if resurrection:
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

    return profile


def test_empty_army_has_zero_defence():
    army = Army()

    assert calculate_army_defensive_combat_score(
        army
    ) == pytest.approx(0.0)

    assert calculate_army_defensive_output_density(
        army
    ) == pytest.approx(0.0)


def test_army_defence_uses_mechanical_profile_score():
    profile = create_profile(points=20)

    army = Army()
    army.add_profile(profile, quantity=1)

    expected_profile_score = (
        calculate_profile_defensive_combat_score(
            profile,
            DEFAULT_COMBAT_BENCHMARK,
            engagements=3,
        )
    )

    result = calculate_army_defensive_combat_score(
        army
    )

    assert result == pytest.approx(
        expected_profile_score
    )


def test_defence_density_is_points_normalised():
    profile = create_profile(points=20)

    army = Army()
    army.add_profile(profile, quantity=2)

    average = calculate_army_defensive_combat_score(
        army
    )

    density = calculate_army_defensive_output_density(
        army
    )

    assert density == pytest.approx(
        average * 5
    )


def test_tougher_models_improve_defence_at_equal_cost():
    ordinary_army = Army()
    tougher_army = Army()

    ordinary_army.add_profile(
        create_profile(
            profile_id="ORDINARY",
            points=30,
            wounds=1,
        ),
        quantity=2,
    )

    tougher_army.add_profile(
        create_profile(
            profile_id="TOUGHER",
            points=30,
            wounds=2,
        ),
        quantity=2,
    )

    assert calculate_army_defensive_output_density(
        tougher_army
    ) > calculate_army_defensive_output_density(
        ordinary_army
    )


def test_resurrection_improves_army_defence():
    ordinary_army = Army()
    resurrection_army = Army()

    ordinary_army.add_profile(
        create_profile(
            profile_id="ORDINARY",
            points=80,
        )
    )

    resurrection_army.add_profile(
        create_profile(
            profile_id="RESURRECTING",
            points=80,
            resurrection=True,
        )
    )

    ordinary_score = (
        calculate_army_defensive_output_density(
            ordinary_army
        )
    )

    resurrection_score = (
        calculate_army_defensive_output_density(
            resurrection_army
        )
    )

    assert resurrection_score > ordinary_score


def test_resurrection_can_be_disabled_for_combat_only():
    army = Army()

    army.add_profile(
        create_profile(
            points=80,
            resurrection=True,
        )
    )

    combat_only = calculate_army_defensive_output_density(
        army,
        include_resurrection=False,
    )

    with_recovery = calculate_army_defensive_output_density(
        army,
        include_resurrection=True,
    )

    assert with_recovery > combat_only


def test_quantity_weighting_matches_manual_calculation():
    ordinary = create_profile(
        profile_id="ORDINARY",
        points=20,
        defence=5,
    )

    tougher = create_profile(
        profile_id="TOUGHER",
        points=40,
        defence=7,
        wounds=2,
    )

    army = Army()
    army.add_profile(ordinary, quantity=3)
    army.add_profile(tougher, quantity=1)

    ordinary_score = calculate_profile_defensive_combat_score(
        ordinary,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
        include_resurrection=True,
    )

    tougher_score = calculate_profile_defensive_combat_score(
        tougher,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
        include_resurrection=True,
    )

    expected = (
        3 * ordinary_score + tougher_score
    ) * 100 / army.total_points()

    assert calculate_army_defensive_output_density(
        army
    ) == pytest.approx(expected)


def test_more_expensive_army_with_same_models_has_lower_density():
    profile = create_profile(points=20)

    baseline = Army()
    baseline.add_profile(profile, quantity=2)

    more_expensive = Army()
    more_expensive.add_profile(profile, quantity=2)
    more_expensive.add_purchase_points(20)

    assert calculate_army_defensive_output_density(
        more_expensive
    ) < calculate_army_defensive_output_density(
        baseline
    )
