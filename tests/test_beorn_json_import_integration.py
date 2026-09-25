from importers.mesbg_list_builder_json_importer import (
    get_imported_configured_entries,
    load_mesbg_list_builder_json,
)
from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from loader import load_all_profiles
from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_form_state import FieldedModelFormState
from fielded_model_form_change_gate import (
    request_fielded_model_form_change,
)
from army import Army
from fielded_model_form_state_initialization import (
    get_initial_fielded_model_form_states,
)
from army_loader import load_factions, load_army_lists
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from siege_engine_profile_loader import (
    load_siege_engine_profiles,
)
from analysis_loader import load_metric_thresholds
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)
import pytest

FIXTURE_PATH = "tests/fixtures/the_beornings.json"


def test_beorn_real_json_preserves_imported_entries():
    data = load_mesbg_list_builder_json(FIXTURE_PATH)

    entries = get_imported_configured_entries(data)

    assert data["armyList"] == "The Beornings"
    assert len(entries) == 4

    assert [
        entry.external_model_id
        for entry in entries
    ] == [
        "[the-beornings] beorn",
        "[the-beornings] beorning",
        "[the-beornings] grimbeorn",
        "[the-beornings] beorning",
    ]

    assert [
        entry.quantity
        for entry in entries
    ] == [1, 2, 1, 2]

    assert entries[3].external_option_ids == (
        "OPT0966",
    )

    assert entries[0].warband_id == entries[1].warband_id
    assert entries[2].warband_id == entries[3].warband_id
    assert entries[0].warband_id != entries[2].warband_id

def test_beorn_real_json_maps_army_and_profiles():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    assert definition.army_list_id == "THE_BEORNINGS"

    assert {
        entry.profile_id: entry.quantity
        for entry in definition.entries
        if entry.profile_id != "BEORNING"
    } == {
        "BEORN": 1,
        "GRIMBEORN": 1,
    }

    beorning_entries = [
        entry
        for entry in definition.entries
        if entry.profile_id == "BEORNING"
    ]

    assert len(beorning_entries) == 2

    assert {
        (entry.external_option_ids, entry.quantity)
        for entry in beorning_entries
    } == {
        ((), 2),
        (("OPT0966",), 2),
    }

def test_beorn_production_man_profile_loads():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    beorn = profiles["BEORN"]

    assert beorn.points == 200
    assert beorn.movement == 6
    assert beorn.base_size_mm == 25
    assert beorn.fight == 6
    assert beorn.strength == 5
    assert beorn.defence == 5
    assert beorn.attacks == 3
    assert beorn.wounds == 3
    assert (beorn.might, beorn.will, beorn.fate) == (
        3, 3, 3
    )
    assert beorn.races == {"MAN"}

def test_beorn_production_bear_profile_loads():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    bear = profiles["BEORN_THE_BEAR"]

    assert bear.points == 0
    assert bear.movement == 8
    assert bear.base_size_mm == 60
    assert bear.fight == 8
    assert bear.strength == 8
    assert bear.defence == 8
    assert bear.attacks == 3
    assert bear.wounds == 3
    assert bear.races == {"BEAR"}

    assert (
        bear.might,
        bear.will,
        bear.fate,
    ) == (3, 3, 3)

def test_imported_beorn_can_transform_using_production_profiles():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    beorn_entry = next(
        entry
        for entry in definition.entries
        if entry.profile_id == "BEORN"
    )

    fielded_beorn = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=profiles[beorn_entry.profile_id],
        ),
    )

    man_state = FieldedModelFormState(
        fielded_model=fielded_beorn,
        active_configured_profile=(
            fielded_beorn.configured_profile
        ),
        allowed_alternate_profile_ids=frozenset(
            {"BEORN_THE_BEAR"}
        ),
    )

    bear_state = request_fielded_model_form_change(
        state=man_state,
        new_active_configured_profile=ConfiguredProfile(
            profile=profiles["BEORN_THE_BEAR"],
        ),
        transition_permitted=True,
    )

    assert bear_state.fielded_model is fielded_beorn
    assert bear_state.fielded_model_id == man_state.fielded_model_id

    assert fielded_beorn.profile_id == "BEORN"
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )

    assert (
        bear_state.active_configured_profile.effective_movement
        == 8
    )
    assert (
        bear_state.active_configured_profile.effective_defence
        == 8
    )
    assert (
        bear_state.active_configured_profile.effective_base_size_mm
        == 60
    )

    returned_state = request_fielded_model_form_change(
        state=bear_state,
        new_active_configured_profile=(
            fielded_beorn.configured_profile
        ),
        transition_permitted=True,
    )

    assert returned_state.fielded_model is fielded_beorn
    assert (
        returned_state.active_configured_profile.profile.id
        == "BEORN"
    )
    assert (
        returned_state.active_configured_profile.effective_base_size_mm
        == 25
    )

def test_beorn_army_initializes_permitted_bear_form():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    army = Army()
    army.add_profile(
        profiles["BEORN"],
        quantity=1,
    )

    states = get_initial_fielded_model_form_states(
        army=army,
        allowed_alternates_by_profile_id={
            "BEORN": frozenset({"BEORN_THE_BEAR"}),
        },
    )

    assert len(states) == 1

    state = states[0]

    assert state.fielded_model.id == army.fielded_models()[0].id
    assert state.fielded_model.profile_id == "BEORN"
    assert (
        state.active_configured_profile.profile.id
        == "BEORN"
    )
    assert state.allowed_alternate_profile_ids == frozenset(
        {"BEORN_THE_BEAR"}
    )

    bear_state = request_fielded_model_form_change(
        state=state,
        new_active_configured_profile=ConfiguredProfile(
            profile=profiles["BEORN_THE_BEAR"],
        ),
        transition_permitted=True,
    )

    assert bear_state.fielded_model is state.fielded_model
    assert bear_state.fielded_model_id == state.fielded_model_id
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )

    assert army.total_points() == 200
    assert army.model_count() == 1

def test_form_initialization_reuses_supplied_fielded_models():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    army = Army()
    army.add_profile(
        profiles["BEORN"],
        quantity=1,
    )

    fielded_models = army.fielded_models()

    states = get_initial_fielded_model_form_states(
        army=army,
        allowed_alternates_by_profile_id={
            "BEORN": frozenset({"BEORN_THE_BEAR"}),
        },
        fielded_models=fielded_models,
    )

    assert len(states) == 1
    assert states[0].fielded_model is fielded_models[0]

def test_beorn_production_alternate_form_mapping():
    from importers.mesbg_list_builder_alternate_form_map import (
        ALLOWED_ALTERNATE_FORMS_BY_PROFILE_ID,
    )

    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    permitted = ALLOWED_ALTERNATE_FORMS_BY_PROFILE_ID["BEORN"]

    assert permitted == frozenset({"BEORN_THE_BEAR"})
    assert all(profile_id in profiles for profile_id in permitted)

@pytest.mark.skip(
    reason=(
        "Deferred to Armies of Middle-earth expansion: "
        "requires complete Beornings army-list production data."
    )
)

def test_beorn_real_json_initializes_forms_through_analysis_service():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(options)
    )

    factions = load_factions()
    army_lists = load_army_lists(factions)

    result = analyse_mesbg_list_builder_file(
        FIXTURE_PATH,
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=(
            options_by_external_id
        ),
        siege_engine_profiles_by_id=(
            load_siege_engine_profiles()
        ),
    )

    army = result["army"]

    assert army.total_points() == 480
    assert army.model_count() == 6

    form_states = result["fielded_model_form_states"]

    assert len(form_states) == 6

    beorn_state = next(
        state
        for state in form_states
        if state.fielded_model.profile_id == "BEORN"
    )

    assert (
        beorn_state.active_configured_profile.profile.id
        == "BEORN"
    )
    assert (
        beorn_state.allowed_alternate_profile_ids
        == frozenset({"BEORN_THE_BEAR"})
    )

    bear_state = request_fielded_model_form_change(
        state=beorn_state,
        new_active_configured_profile=ConfiguredProfile(
            profile=profiles["BEORN_THE_BEAR"],
        ),
        transition_permitted=True,
    )

    assert (
        bear_state.fielded_model
        is beorn_state.fielded_model
    )
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )

    assert army.total_points() == 480
    assert army.model_count() == 6