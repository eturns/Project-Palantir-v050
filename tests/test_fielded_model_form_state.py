from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_form_state import FieldedModelFormState
from profiles import Profile
from fielded_model_form_transition import change_fielded_model_form
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from resource_owner import ResourceOwner
from profile_classification import ModelType

def make_profile(
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
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_fielded_model_form_state_preserves_fielded_identity():
    man_profile = make_profile("BEORN")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    assert state.fielded_model_id == "BEORN:1:1"
    assert state.fielded_model is fielded_model

def test_fielded_model_form_state_can_use_alternate_profile():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    bear_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert bear_state.fielded_model_id == "BEORN:1:1"
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )
    assert (
        bear_state.fielded_model.configured_profile.profile.id
        == "BEORN"
    )

def test_change_fielded_model_form_preserves_fielded_model_identity():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert bear_state.fielded_model is fielded_model
    assert bear_state.fielded_model_id == "BEORN:1:1"
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )

def test_form_change_preserves_resources_owned_by_fielded_identity():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    resources = OwnedHeroResourceState(
        owner=ResourceOwner(
            fielded_model_id=fielded_model.id,
        ),
        resources=HeroResourceState(
            remaining_might=2,
            remaining_will=1,
            remaining_fate=3,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert resources.owner.fielded_model_id == (
        bear_state.fielded_model_id
    )
    assert resources.resources == HeroResourceState(
        remaining_might=2,
        remaining_will=1,
        remaining_fate=3,
    )

def test_form_change_changes_effective_profile_without_mutating_base():
    man_profile = make_profile("BEORN")

    bear_profile = Profile(
        id="BEORN_THE_BEAR",
        name="Beorn the Bear",
        points=0,
        movement=8,
        fight=8,
        shooting="4+",
        strength=8,
        defence=8,
        attacks=3,
        wounds=3,
        courage="3+",
        intelligence="6+",
        might=3,
        will=3,
        fate=3,
        max_in_army=1,
    )

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert (
        bear_state.active_configured_profile.effective_movement
        == 8
    )
    assert (
        bear_state.active_configured_profile.profile.strength
        == 8
    )
    assert (
        bear_state.active_configured_profile.effective_defence
        == 8
    )

    assert (
        fielded_model.configured_profile.profile.id
        == "BEORN"
    )
    assert (
        man_state.active_configured_profile.profile.id
        == "BEORN"
    )

def test_fielded_model_can_change_form_back_to_original_profile():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    returned_man_state = change_fielded_model_form(
        bear_state,
        fielded_model.configured_profile,
    )

    assert returned_man_state.fielded_model is fielded_model
    assert returned_man_state.fielded_model_id == "BEORN:1:1"
    assert (
        returned_man_state.active_configured_profile.profile.id
        == "BEORN"
    )

def test_form_change_updates_base_size_and_model_types():
    man_profile = Profile(
        id="BEORN",
        name="Beorn",
        points=200,
        movement=6,
        base_size_mm=25,
        fight=6,
        shooting="4+",
        strength=5,
        defence=5,
        attacks=3,
        wounds=3,
        courage="3+",
        intelligence="4+",
        might=3,
        will=3,
        fate=3,
        max_in_army=1,
        model_types={
            ModelType.INFANTRY,
        },
    )

    bear_profile = Profile(
        id="BEORN_THE_BEAR",
        name="Beorn the Bear",
        points=0,
        movement=8,
        base_size_mm=60,
        fight=8,
        shooting="4+",
        strength=8,
        defence=8,
        attacks=3,
        wounds=3,
        courage="3+",
        intelligence="6+",
        might=3,
        will=3,
        fate=3,
        max_in_army=1,
        model_types={
            ModelType.INFANTRY,
            ModelType.MONSTER,
        },
    )

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert (
        man_state.active_configured_profile.effective_base_size_mm
        == 25
    )
    assert (
        bear_state.active_configured_profile.effective_base_size_mm
        == 60
    )
    assert (
        man_state.active_configured_profile.effective_model_types
        == {
            ModelType.INFANTRY,
        }
    )
    assert (
        bear_state.active_configured_profile.effective_model_types
        == {
            ModelType.INFANTRY,
            ModelType.MONSTER,
        }
    )

def test_form_change_updates_active_race():
    man_profile = make_profile("BEORN")
    man_profile.races = {"MAN"}

    bear_profile = make_profile("BEORN_THE_BEAR")
    bear_profile.races = {"BEAR"}

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert (
        man_state.active_configured_profile.profile.races
        == {"MAN"}
    )
    assert (
        bear_state.active_configured_profile.profile.races
        == {"BEAR"}
    )

def test_active_form_does_not_replace_roster_profile_identity():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
    )

    bear_state = change_fielded_model_form(
        man_state,
        ConfiguredProfile(
            profile=bear_profile,
        ),
    )

    assert fielded_model.profile_id == "BEORN"
    assert bear_state.fielded_model.profile_id == "BEORN"
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )