from army import Army
from profile_classification import (
    HeroicStatus,
)
from profiles import Profile
from scenario_preservation_profile import (
    get_fog_of_war_preservation_profiles,
    select_fog_of_war_preservation_profile,
)


def build_profile(
    profile_id: str,
    *,
    heroic_status: HeroicStatus,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=1,
        heroic_status=heroic_status,
    )


def test_fog_of_war_preservation_profiles_exclude_leader():
    army = Army()

    leader = build_profile(
        "LEADER",
        heroic_status=HeroicStatus.HERO,
    )

    other_hero = build_profile(
        "OTHER_HERO",
        heroic_status=HeroicStatus.HERO,
    )

    warrior = build_profile(
        "WARRIOR",
        heroic_status=HeroicStatus.WARRIOR,
    )

    army.add_profile(
        leader,
        quantity=1,
    )

    army.add_profile(
        other_hero,
        quantity=1,
    )

    army.add_profile(
        warrior,
        quantity=1,
    )

    result = get_fog_of_war_preservation_profiles(
        army=army,
        leader_profile=leader,
    )

    assert result == (
        other_hero,
    )

def test_fog_of_war_selects_best_eligible_preservation_profile(
    monkeypatch,
):
    army = Army()

    leader = build_profile(
        "LEADER",
        heroic_status=HeroicStatus.HERO,
    )

    weaker_hero = build_profile(
        "WEAKER_HERO",
        heroic_status=HeroicStatus.HERO,
    )

    stronger_hero = build_profile(
        "STRONGER_HERO",
        heroic_status=HeroicStatus.HERO,
    )

    warrior = build_profile(
        "WARRIOR",
        heroic_status=HeroicStatus.WARRIOR,
    )

    army.add_profile(leader)
    army.add_profile(weaker_hero)
    army.add_profile(stronger_hero)
    army.add_profile(warrior)

    scores = {
        "WEAKER_HERO": 0.40,
        "STRONGER_HERO": 0.75,
    }

    def fake_calculate_preservation(
        profile,
        benchmark,
        benchmark_fate,
    ):
        class Result:
            value = scores[profile.id]

        return Result()

    monkeypatch.setattr(
        "scenario_preservation_profile."
        "calculate_key_model_preservation_from_profile",
        fake_calculate_preservation,
    )

    result = select_fog_of_war_preservation_profile(
        army=army,
        leader_profile=leader,
        combat_benchmark="BENCHMARK",
        benchmark_fate=2.0,
    )

    assert result is stronger_hero