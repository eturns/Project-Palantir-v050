from army import Army
from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus
from profiles import Profile
from scenario_preservation_profile import (
    get_fog_of_war_preservation_models,
    select_fog_of_war_preservation_model,
)


def make_profile(
    *,
    profile_id: str,
    heroic_status: HeroicStatus,
    fate: int = 1,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage=4,
        intelligence="4+",
        might=1,
        will=1,
        fate=fate,
        max_in_army=0,
        heroic_status=heroic_status,
    )


def test_leader_model_is_excluded_but_identical_copy_remains_eligible():
    profile = make_profile(
        profile_id="GENERIC_HERO",
        heroic_status=HeroicStatus.HERO,
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    fielded_models = army.fielded_models()

    leader_model = fielded_models[0]

    eligible_models = get_fog_of_war_preservation_models(
        army=army,
        leader_model=leader_model,
    )

    assert eligible_models == (
        fielded_models[1],
    )


def test_non_hero_models_are_not_eligible():
    hero = make_profile(
        profile_id="HERO",
        heroic_status=HeroicStatus.HERO,
    )

    warrior = make_profile(
        profile_id="WARRIOR",
        heroic_status=HeroicStatus.WARRIOR,
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=hero,
        ),
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=warrior,
        ),
    )

    fielded_models = army.fielded_models()

    eligible_models = get_fog_of_war_preservation_models(
        army=army,
        leader_model=fielded_models[0],
    )

    assert eligible_models == ()


def test_different_configurations_of_same_profile_remain_distinct():
    profile = make_profile(
        profile_id="GENERIC_HERO",
        heroic_status=HeroicStatus.HERO,
    )

    first_configuration = ConfiguredProfile(
        profile=profile,
    )

    second_configuration = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        first_configuration,
    )

    army.add_configured_profile(
        second_configuration,
    )

    fielded_models = army.fielded_models()

    eligible_models = get_fog_of_war_preservation_models(
        army=army,
        leader_model=fielded_models[0],
    )

    assert eligible_models == (
        fielded_models[1],
    )

    assert (
        eligible_models[0].configured_profile
        is second_configuration
    )


def test_preservation_selection_returns_fielded_model(monkeypatch):
    leader_profile = make_profile(
        profile_id="LEADER",
        heroic_status=HeroicStatus.HERO,
    )

    other_profile = make_profile(
        profile_id="OTHER_HERO",
        heroic_status=HeroicStatus.HERO,
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=leader_profile,
        ),
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=other_profile,
        ),
    )

    fielded_models = army.fielded_models()

    class FakeCapability:
        value = 0.5

    monkeypatch.setattr(
        "scenario_preservation_profile."
        "calculate_key_model_preservation_from_profile",
        lambda **kwargs: FakeCapability(),
    )

    selected_model = select_fog_of_war_preservation_model(
        army=army,
        leader_model=fielded_models[0],
        combat_benchmark=object(),
        benchmark_fate=1,
    )

    assert selected_model == fielded_models[1]