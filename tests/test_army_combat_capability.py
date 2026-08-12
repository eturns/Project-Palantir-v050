import pytest

import army_combat_capability

from army import Army
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from profiles import Profile


def create_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
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
        max_in_army=99,
    )


def test_army_combat_capability_uses_quantity_weighted_mean(
    monkeypatch,
):
    strong = create_profile(
        "STRONG",
    )

    weak = create_profile(
        "WEAK",
    )

    army = Army()

    army.add_profile(
        strong,
        quantity=1,
    )

    army.add_profile(
        weak,
        quantity=3,
    )

    def fake_profile_score(
        profile,
        benchmark,
    ):
        if profile.id == "STRONG":
            return 0.8

        return 0.4

    monkeypatch.setattr(
        army_combat_capability,
        "calculate_profile_combat_capability",
        fake_profile_score,
    )

    score = (
        army_combat_capability
        .calculate_army_combat_capability(
            army,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert score == pytest.approx(
        0.5,
    )


def test_army_combat_capability_returns_zero_for_empty_army():
    army = Army()

    score = (
        army_combat_capability
        .calculate_army_combat_capability(
            army,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert score == 0.0