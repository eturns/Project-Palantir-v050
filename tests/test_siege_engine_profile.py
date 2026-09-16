from siege_engine_profile import SiegeEngineProfile
from fielded_model import FieldedModel
from army import Army
from profiles import Profile
from army_model_state_initialization import (
    get_initial_army_model_state,
)
from army_quarter_strength_state import (
    calculate_quarter_strength,
)
from army_break_state import calculate_break_point
from configured_profile import ConfiguredProfile
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_builder import (
    build_fielded_model_structures,
)
from fielded_model_structure_definition import (
    FieldedModelStructureDefinition,
)
from fielded_model_structure_member import (
    FieldedModelStructureMember,
)

def test_siege_engine_profile_stores_only_siege_characteristics():
    profile = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    assert profile.id == "IH_BALLISTA"
    assert profile.range_min == 12
    assert profile.range_max == 60
    assert profile.strength == 8
    assert profile.defence == 10
    assert profile.wounds == 4

def test_siege_engine_can_become_a_fielded_model():
    profile = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    model = FieldedModel(
        id="IH_BALLISTA:1:1",
        siege_engine_profile=profile,
        warband_id="WARBAND_A",
    )

    assert model.id == "IH_BALLISTA:1:1"
    assert model.siege_engine_profile is profile

def test_fielded_siege_engine_does_not_count_as_model():
    profile = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    model = FieldedModel(
        id="IH_BALLISTA:1:1",
        siege_engine_profile=profile,
        warband_id="WARBAND_A",
    )

    assert model.counts_as_model is False

def test_army_model_count_excludes_siege_engine():
    crew_profile = Profile(
        id="IH_SIEGE_CREW",
        name="Iron Hills Siege Crew",
        points=0,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    army = Army()

    army.add_profile(
        crew_profile,
        quantity=4,
        warband_id="WARBAND_A",
    )

    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    army.add_siege_engine_profile(
        ballista,
        quantity=1,
        warband_id="WARBAND_A",
    )

    assert army.model_count() == 4

def test_initial_army_model_state_excludes_siege_engine():
    crew_profile = Profile(
        id="IH_SIEGE_CREW",
        name="Iron Hills Siege Crew",
        points=0,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    army = Army()

    army.add_profile(
        crew_profile,
        quantity=4,
        warband_id="WARBAND_A",
    )

    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    army.add_siege_engine_profile(
        ballista,
        quantity=1,
        warband_id="WARBAND_A",
    )

    state = get_initial_army_model_state(army)

    assert state.starting_models == 4

def test_quarter_strength_excludes_siege_engine():
    crew_profile = Profile(
        id="IH_SIEGE_CREW",
        name="Iron Hills Siege Crew",
        points=0,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    army = Army()

    army.add_profile(
        crew_profile,
        quantity=4,
        warband_id="WARBAND_A",
    )

    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    army.add_siege_engine_profile(
        ballista,
        quantity=1,
        warband_id="WARBAND_A",
    )

    state = get_initial_army_model_state(army)

    result = calculate_quarter_strength(
        state.starting_models,
    )

    assert result == 1

def test_break_point_excludes_siege_engine():
    crew_profile = Profile(
        id="IH_SIEGE_CREW",
        name="Iron Hills Siege Crew",
        points=0,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    army = Army()

    army.add_profile(
        crew_profile,
        quantity=4,
        warband_id="WARBAND_A",
    )

    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    army.add_siege_engine_profile(
        ballista,
        quantity=1,
        warband_id="WARBAND_A",
    )

    state = get_initial_army_model_state(army)

    assert calculate_break_point(
        state.starting_models,
    ) == 2

def test_army_expands_siege_engine_to_fielded_model():
    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    army = Army()

    army.add_siege_engine_profile(
        ballista,
        warband_id="WARBAND_A",
    )

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 1

    assert (
        fielded_models[0].siege_engine_profile
        is ballista
    )

    assert fielded_models[0].id == "IH_BALLISTA:1:1"

def test_fielded_siege_engine_exposes_profile_id():
    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    model = FieldedModel(
        id="IH_BALLISTA:1:1",
        siege_engine_profile=ballista,
        warband_id="WARBAND_A",
    )

    assert model.profile_id == "IH_BALLISTA"

def test_siege_engine_root_links_four_separate_crew():
    ballista_profile = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    crew_profile = Profile(
        id="IH_SIEGE_CREW",
        name="Iron Hills Siege Crew",
        points=0,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    ballista = FieldedModel(
        id="IH_BALLISTA:1:1",
        siege_engine_profile=ballista_profile,
        warband_id="WARBAND_A",
    )

    crew_models = tuple(
        FieldedModel(
            id=f"IH_SIEGE_CREW:2:{index}",
            configured_profile=ConfiguredProfile(
                profile=crew_profile,
            ),
            warband_id="WARBAND_A",
        )
        for index in range(1, 5)
    )

    definition = FieldedModelStructureDefinition(
        root_profile_id="IH_BALLISTA",
        members=tuple(
            FieldedModelStructureMember(
                profile_id="IH_SIEGE_CREW",
                relationship_type=(
                    FieldedModelRelationshipType.CREW_OF
                ),
            )
            for _ in range(4)
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(
            ballista,
            *crew_models,
        ),
        structure_definitions={
            "IH_BALLISTA": definition,
        },
        profiles_by_id={
            "IH_SIEGE_CREW": crew_profile,
        },
    )

    assert len(result.relationships) == 4

    assert {
        relationship.source_fielded_model_id
        for relationship in result.relationships
    } == {
        crew.id
        for crew in crew_models
    }

    assert {
        relationship.target_fielded_model_id
        for relationship in result.relationships
    } == {
        ballista.id
    }