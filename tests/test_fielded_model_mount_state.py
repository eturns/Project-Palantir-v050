import pytest

from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_form_state import (
    FieldedModelFormState,
)
from fielded_model_mount_transition import (
    dismount_fielded_model,
)
from mount import Mount
from profile_classification import ModelType
from profiles import Profile


def make_rider() -> Profile:
    return Profile(
        id="TEST_RIDER",
        name="Test Rider",
        points=20,
        movement=6,
        base_size_mm=25,
        fight=3,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={
            ModelType.CAVALRY,
        },
    )


def make_warg() -> Mount:
    return Mount(
        id="MOUNT_WARG",
        name="Warg",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="8+",
        intelligence="8+",
        base_size_mm=40,
        races=frozenset(
            {
                "WARG",
            }
        ),
    )


def make_mounted_state():
    profile = make_rider()
    profile.default_mount = make_warg()

    configured = ConfiguredProfile(
        profile=profile,
    )

    fielded_model = FieldedModel(
        id="TEST_RIDER:1",
        configured_profile=configured,
    )

    return FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=configured,
    )


def test_mounted_state_uses_mount_characteristics():
    state = make_mounted_state()

    assert state.has_active_mount is True
    assert state.effective_movement == 10
    assert state.effective_fight == 3
    assert state.effective_strength == 4
    assert state.effective_attacks == 1
    assert state.effective_base_size_mm == 40
    assert state.effective_model_types == {
        ModelType.CAVALRY,
    }


def test_dismounted_state_uses_rider_characteristics():
    mounted_state = make_mounted_state()

    dismounted_state = dismount_fielded_model(
        mounted_state
    )

    assert dismounted_state.has_active_mount is False
    assert dismounted_state.effective_movement == 6
    assert dismounted_state.effective_fight == 3
    assert dismounted_state.effective_strength == 3
    assert dismounted_state.effective_attacks == 1
    assert dismounted_state.effective_base_size_mm == 25

    assert dismounted_state.effective_model_types == {
        ModelType.INFANTRY,
    }


def test_dismount_does_not_change_purchased_configuration():
    mounted_state = make_mounted_state()

    dismounted_state = dismount_fielded_model(
        mounted_state
    )

    assert (
        dismounted_state
        .active_configured_profile
        .effective_mount
        is not None
    )

    assert (
        dismounted_state.fielded_model
        is mounted_state.fielded_model
    )


def test_cannot_dismount_twice():
    state = make_mounted_state()

    state = dismount_fielded_model(
        state
    )

    with pytest.raises(
        ValueError,
        match="already dismounted",
    ):
        dismount_fielded_model(
            state
        )