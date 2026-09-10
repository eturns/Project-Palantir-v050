from dataclasses import FrozenInstanceError

import pytest

from army import Army
from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from profiles import Profile


def make_profile(
    *,
    profile_id: str = "TEST_PROFILE",
) -> Profile:
    return Profile(
        id=profile_id,
        name="Test Profile",
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage=3,
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_fielded_model_is_immutable():
    configured_profile = ConfiguredProfile(
        profile=make_profile(),
    )

    model = FieldedModel(
        id="TEST_PROFILE:1:1",
        configured_profile=configured_profile,
    )

    with pytest.raises(FrozenInstanceError):
        model.id = "CHANGED"


def test_army_expands_quantity_into_distinct_fielded_models():
    profile = make_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=3,
    )

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 3

    assert tuple(
        model.id
        for model in fielded_models
    ) == (
        "TEST_PROFILE:1:1",
        "TEST_PROFILE:1:2",
        "TEST_PROFILE:1:3",
    )


def test_fielded_models_from_same_entry_share_configured_profile():
    profile = make_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        configured_profile,
        quantity=2,
    )

    fielded_models = army.fielded_models()

    assert (
        fielded_models[0].configured_profile
        is configured_profile
    )

    assert (
        fielded_models[1].configured_profile
        is configured_profile
    )


def test_same_profile_with_different_configurations_gets_distinct_identity():
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
    )

    army.add_configured_profile(
        second_configuration,
    )

    fielded_models = army.fielded_models()

    assert tuple(
        model.id
        for model in fielded_models
    ) == (
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:2:1",
    )

    assert (
        fielded_models[0].configured_profile
        is first_configuration
    )

    assert (
        fielded_models[1].configured_profile
        is second_configuration
    )


def test_fielded_model_ids_are_deterministic_for_fixed_army_order():
    first_profile = make_profile(
        profile_id="PROFILE_A",
    )

    second_profile = make_profile(
        profile_id="PROFILE_B",
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=first_profile,
        ),
        quantity=2,
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=second_profile,
        ),
    )

    first_expansion = army.fielded_models()
    second_expansion = army.fielded_models()

    assert tuple(
        model.id
        for model in first_expansion
    ) == tuple(
        model.id
        for model in second_expansion
    )

def test_same_profile_same_configuration_quantity_has_unique_ids():
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

    fielded_models = army.fielded_models()

    ids = tuple(
        model.id
        for model in fielded_models
    )

    assert ids == (
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:1:2",
        "GENERIC_HERO:1:3",
    )

    assert len(set(ids)) == 3


def test_same_profile_multiple_configurations_have_no_identity_collisions():
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

    fielded_models = army.fielded_models()

    ids = tuple(
        model.id
        for model in fielded_models
    )

    assert ids == (
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:1:2",
        "GENERIC_HERO:2:1",
        "GENERIC_HERO:2:2",
    )

    assert len(set(ids)) == 4


def test_different_profiles_have_distinct_fielded_identity():
    first_profile = make_profile(
        profile_id="PROFILE_A",
    )

    second_profile = make_profile(
        profile_id="PROFILE_B",
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=first_profile,
        ),
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=second_profile,
        ),
    )

    fielded_models = army.fielded_models()

    assert tuple(
        model.id
        for model in fielded_models
    ) == (
        "PROFILE_A:1:1",
        "PROFILE_B:2:1",
    )

    assert len(
        {
            model.id
            for model in fielded_models
        }
    ) == 2


def test_repeated_fielded_model_expansion_preserves_identity_order():
    profile = make_profile(
        profile_id="TEST_PROFILE",
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=profile,
        ),
        quantity=3,
    )

    first_ids = tuple(
        model.id
        for model in army.fielded_models()
    )

    second_ids = tuple(
        model.id
        for model in army.fielded_models()
    )

    assert first_ids == second_ids


def test_fielded_model_count_matches_army_model_count():
    first_profile = make_profile(
        profile_id="PROFILE_A",
    )

    second_profile = make_profile(
        profile_id="PROFILE_B",
    )

    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=first_profile,
        ),
        quantity=2,
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=second_profile,
        ),
        quantity=3,
    )

    assert len(
        army.fielded_models()
    ) == army.model_count()

def test_fielded_model_preserves_warband_id():
    configured_profile = ConfiguredProfile(
        profile=make_profile(),
    )

    model = FieldedModel(
        id="TEST_PROFILE:1:1",
        configured_profile=configured_profile,
        warband_id="WARBAND_A",
    )

    assert model.warband_id == "WARBAND_A"

def test_army_fielded_models_preserve_warband_id():
    profile = make_profile()

    army = Army()
    army.add_profile(
        profile,
        quantity=2,
        warband_id="WARBAND_A",
    )

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 2
    assert fielded_models[0].warband_id == (
        "WARBAND_A"
    )
    assert fielded_models[1].warband_id == (
        "WARBAND_A"
    )