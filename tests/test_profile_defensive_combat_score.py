"""DEV-077S-I2-C-G4 defensive survivability regression."""

import pytest

import profile_defensive_combat_score as defence_module

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
from wargear import Wargear


def create_profile(
    *,
    fight: int,
    defence: int,
    attacks: int,
    wounds: int = 1,
    fate: int = 0,
) -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=0,
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
        max_in_army=1,
    )


def score(profile, engagements=1):
    return calculate_profile_defensive_combat_score(
        profile,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=engagements,
    )


def test_profile_defensive_combat_score_reflects_resistance_to_benchmark():
    profile = create_profile(
        fight=4, defence=6, attacks=1
    )
    assert score(profile) == pytest.approx(5 / 6)


def test_higher_defence_improves_defensive_combat_score():
    d5 = create_profile(fight=4, defence=5, attacks=1)
    d7 = create_profile(fight=4, defence=7, attacks=1)
    assert score(d7) > score(d5)


def test_more_attacks_improve_defensive_combat_score_through_duel_resistance():
    a1 = create_profile(fight=4, defence=6, attacks=1)
    a2 = create_profile(fight=4, defence=6, attacks=2)
    assert score(a2) > score(a1)


def test_extra_wounds_improve_defensive_survivability():
    w1 = create_profile(
        fight=4, defence=6, attacks=1, wounds=1
    )
    w3 = create_profile(
        fight=4, defence=6, attacks=1, wounds=3
    )
    assert score(w3) > score(w1)


def test_repeated_engagements_reduce_survival_probability():
    profile = create_profile(
        fight=4, defence=6, attacks=1
    )
    assert 0 < score(profile, 3) < score(profile, 1) < 1


def test_three_wound_model_loses_survivability_across_engagements():
    profile = create_profile(
        fight=4, defence=6, attacks=1, wounds=3
    )
    assert score(profile, 1) == pytest.approx(1.0)
    assert 0 < score(profile, 3) < score(profile, 1)


def test_fate_improves_survival_across_repeated_engagements():
    f0 = create_profile(
        fight=4, defence=6, attacks=1, fate=0
    )
    f1 = create_profile(
        fight=4, defence=6, attacks=1, fate=1
    )
    assert score(f0, 3) < score(f1, 3) < 1.0


def test_one_fate_point_prevents_at_most_one_wound():
    f0 = create_profile(
        fight=4, defence=6, attacks=1, fate=0
    )
    f1 = create_profile(
        fight=4, defence=6, attacks=1, fate=1
    )

    assert score(f0, 3) == pytest.approx((5 / 6) ** 3)
    assert score(f1, 1) == pytest.approx(11 / 12)
    assert score(f0, 3) < score(f1, 3) < score(f1, 1)


def test_additional_fate_improves_survival_over_three_engagements():
    f1 = create_profile(
        fight=4, defence=6, attacks=1, fate=1
    )
    f2 = create_profile(
        fight=4, defence=6, attacks=1, fate=2
    )

    assert score(f2, 3) > score(f1, 3)
    assert score(f2, 3) < 1.0


def test_multi_wound_model_can_conserve_fate_until_it_matters():
    f0 = create_profile(
        fight=4, defence=6, attacks=1,
        wounds=3, fate=0,
    )
    f1 = create_profile(
        fight=4, defence=6, attacks=1,
        wounds=3, fate=1,
    )

    assert score(f0, 2) == pytest.approx(1.0)
    assert score(f1, 2) == pytest.approx(1.0)
    assert score(f1, 3) > score(f0, 3)


def test_engagement_count_must_be_positive_integer():
    profile = create_profile(
        fight=4, defence=6, attacks=1
    )

    for invalid in (0, -1, 1.5, True):
        with pytest.raises(ValueError):
            score(profile, invalid)


def test_two_handed_weapon_reduces_defensive_survivability():
    ordinary_profile = create_profile(
        fight=4, defence=6, attacks=1
    )
    two_handed_profile = create_profile(
        fight=4, defence=6, attacks=1
    )

    two_handed_profile.default_wargear.append(
        Wargear(
            id="WG_TWO_HANDED_WEAPON",
            name="Two-handed Weapon",
        )
    )

    ordinary = ConfiguredProfile(
        profile=ordinary_profile
    )
    two_handed = ConfiguredProfile(
        profile=two_handed_profile
    )

    assert score(two_handed, 3) < score(ordinary, 3)


def test_burly_cancels_two_handed_defensive_duel_penalty():
    ordinary_profile = create_profile(
        fight=4, defence=6, attacks=1
    )
    two_handed_profile = create_profile(
        fight=4, defence=6, attacks=1
    )
    burly_profile = create_profile(
        fight=4, defence=6, attacks=1
    )

    weapon = Wargear(
        id="WG_TWO_HANDED_WEAPON",
        name="Two-handed Weapon",
    )

    two_handed_profile.default_wargear.append(weapon)
    burly_profile.default_wargear.append(weapon)

    burly_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="BURLY",
                name="Burly",
                category=RuleCategory.SPECIAL,
            ),
            parameter=None,
        )
    )

    ordinary = ConfiguredProfile(
        profile=ordinary_profile
    )
    two_handed = ConfiguredProfile(
        profile=two_handed_profile
    )
    burly = ConfiguredProfile(
        profile=burly_profile
    )

    assert score(two_handed, 3) < score(ordinary, 3)
    assert score(burly, 3) == pytest.approx(
        score(ordinary, 3)
    )


def test_configured_defence_uses_configured_wound_engine(
    monkeypatch,
):
    defender = ConfiguredProfile(
        profile=create_profile(
            fight=4,
            defence=6,
            attacks=1,
        )
    )

    calls = []

    def fake_configured_wound_probability(
        attacker,
        defender,
        **kwargs,
    ):
        calls.append((attacker, defender))
        return 0.0

    monkeypatch.setattr(
        defence_module,
        "calculate_configured_wound_probability",
        fake_configured_wound_probability,
        raising=False,
    )

    result = score(defender, engagements=3)

    # Zero chance to wound means guaranteed survival.
    assert result == pytest.approx(1.0)

    # Verify the attacker/defender orientation.
    assert calls
    assert all(
        actual_defender is defender
        for _, actual_defender in calls
    )

    assert all(
        actual_attacker.profile.id
        == "DEFENCE_BENCHMARK"
        for actual_attacker, _ in calls
    )
