from types import SimpleNamespace

from army import Army
from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus
from profiles import Profile
from scenario_preservation_profile import (
    get_fog_of_war_preservation_models,
)


def make_profile(
    *,
    profile_id: str,
    heroic_status: HeroicStatus = HeroicStatus.HERO,
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
        fate=1,
        max_in_army=0,
        heroic_status=heroic_status,
    )


def test_dev062_quantity_expands_to_unique_fielded_models():
    profile = make_profile(
        profile_id="GENERIC_HERO",
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=3,
    )

    models = army.fielded_models()

    assert len(models) == 3

    assert tuple(
        model.id
        for model in models
    ) == (
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:1:2",
        "GENERIC_HERO:1:3",
    )

    assert len(
        {
            model.id
            for model in models
        }
    ) == 3


def test_dev062_same_profile_different_configurations_remain_distinct():
    profile = make_profile(
        profile_id="GENERIC_HERO",
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
        quantity=2,
    )

    army.add_configured_profile(
        second_configuration,
        quantity=2,
    )

    models = army.fielded_models()

    assert len(models) == 4

    assert tuple(
        model.id
        for model in models
    ) == (
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:1:2",
        "GENERIC_HERO:2:1",
        "GENERIC_HERO:2:2",
    )

    assert models[0].configured_profile is first_configuration
    assert models[1].configured_profile is first_configuration

    assert models[2].configured_profile is second_configuration
    assert models[3].configured_profile is second_configuration


def test_dev062_one_identical_copy_can_be_leader_while_other_remains_eligible():
    profile = make_profile(
        profile_id="GENERIC_HERO",
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    models = army.fielded_models()

    leader_model = models[0]

    eligible_models = (
        get_fog_of_war_preservation_models(
            army=army,
            leader_model=leader_model,
        )
    )

    assert eligible_models == (
        models[1],
    )

    assert eligible_models[0].id != leader_model.id


def test_dev062_fielded_model_contains_identity_not_runtime_state():
    profile = make_profile(
        profile_id="GENERIC_HERO",
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=profile,
        ),
    )

    model = army.fielded_models()[0]

    assert hasattr(model, "id")
    assert hasattr(model, "configured_profile")

    assert not hasattr(model, "remaining_might")
    assert not hasattr(model, "remaining_will")
    assert not hasattr(model, "remaining_fate")
    assert not hasattr(model, "remaining_wounds")
    assert not hasattr(model, "alive")