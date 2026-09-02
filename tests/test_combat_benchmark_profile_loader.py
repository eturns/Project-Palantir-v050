from combat_benchmark_profile_loader import (
    load_combat_benchmark_profiles,
)
from profiles import Profile


def test_loads_ten_combat_benchmark_profiles():
    profiles = load_combat_benchmark_profiles()

    assert len(profiles) == 10
    assert all(
        isinstance(profile, Profile)
        for profile in profiles
    )


def test_loads_elrond_as_full_profile():
    profiles = load_combat_benchmark_profiles()

    elrond = next(
        profile
        for profile in profiles
        if profile.id == "BENCH_ELROND"
    )

    assert elrond.name == "Elrond, Master of Rivendell"
    assert elrond.points == 170
    assert elrond.movement == 6
    assert elrond.base_size_mm == 25
    assert elrond.fight == 7
    assert elrond.shooting == "3+"
    assert elrond.strength == 4
    assert elrond.defence == 7
    assert elrond.attacks == 3
    assert elrond.wounds == 3
    assert elrond.courage == "3+"
    assert elrond.intelligence == "3+"
    assert elrond.might == 3
    assert elrond.will == 3
    assert elrond.fate == 3
    assert elrond.max_in_army == 1