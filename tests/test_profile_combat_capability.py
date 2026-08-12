import pytest

import profile_combat_capability

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from profiles import Profile


def create_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test",
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
        max_in_army=1,
    )


def test_profile_combat_capability_uses_equal_offence_defence_weighting(
    monkeypatch,
):
    profile = create_profile()

    monkeypatch.setattr(
        profile_combat_capability,
        "calculate_profile_offensive_combat_score",
        lambda profile, benchmark: 0.2,
    )

    monkeypatch.setattr(
        profile_combat_capability,
        "calculate_profile_defensive_combat_score",
        lambda profile, benchmark: 0.8,
    )

    score = (
        profile_combat_capability
        .calculate_profile_combat_capability(
            profile,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert score == pytest.approx(0.5)


def test_profile_combat_capability_preserves_uniform_components(
    monkeypatch,
):
    profile = create_profile()

    monkeypatch.setattr(
        profile_combat_capability,
        "calculate_profile_offensive_combat_score",
        lambda profile, benchmark: 0.6,
    )

    monkeypatch.setattr(
        profile_combat_capability,
        "calculate_profile_defensive_combat_score",
        lambda profile, benchmark: 0.6,
    )

    score = (
        profile_combat_capability
        .calculate_profile_combat_capability(
            profile,
            DEFAULT_COMBAT_BENCHMARK,
        )
    )

    assert score == pytest.approx(0.6)