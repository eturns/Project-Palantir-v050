import pytest

from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
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
from profiles import Profile
from importers.mesbg_list_builder_fielded_structure_map import (
    FIELDED_MODEL_STRUCTURE_DEFINITIONS,
)

def make_profile(
    profile_id: str,
    name: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=name,
        points=0,
        movement=6,
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

def make_fielded_model(
    fielded_model_id: str,
    profile_id: str,
    warband_id: str | None = None,
) -> FieldedModel:
    return FieldedModel(
        id=fielded_model_id,
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                profile_id,
                profile_id,
            ),
        ),
        warband_id=warband_id,
    )

def test_structure_builder_links_existing_member():
    mumak = make_profile(
        "WAR_MUMAK",
        "War Mumak",
    )
    commander = make_profile(
        "COMMANDER",
        "Haradrim Commander",
    )

    root_model = FieldedModel(
        id="WAR_MUMAK:1:1",
        configured_profile=ConfiguredProfile(
            profile=mumak,
        ),
        warband_id="WARBAND_A",
    )

    commander_model = FieldedModel(
        id="COMMANDER:2:1",
        configured_profile=ConfiguredProfile(
            profile=commander,
        ),
        warband_id="WARBAND_A",
    )

    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(
            FieldedModelStructureMember(
                profile_id="COMMANDER",
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(
            root_model,
            commander_model,
        ),
        structure_definitions={
            "WAR_MUMAK": definition,
        },
        profiles_by_id={
            "WAR_MUMAK": mumak,
            "COMMANDER": commander,
        },
    )

    assert result.fielded_models == (
        root_model,
        commander_model,
    )

    assert len(result.relationships) == 1

    relationship = result.relationships[0]

    assert (
        relationship.source_fielded_model_id
        == commander_model.id
    )
    assert (
        relationship.target_fielded_model_id
        == root_model.id
    )
    assert relationship.relationship_type is (
        FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )


def test_structure_builder_leaves_unknown_root_unchanged():
    profile = make_profile(
        "ORDINARY_MODEL",
        "Ordinary Model",
    )

    model = FieldedModel(
        id="ORDINARY_MODEL:1:1",
        configured_profile=ConfiguredProfile(
            profile=profile,
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(model,),
        structure_definitions={},
        profiles_by_id={
            "ORDINARY_MODEL": profile,
        },
    )

    assert result.fielded_models == (model,)
    assert result.relationships == ()


def test_structure_builder_rejects_unknown_member_profile():
    mumak = make_profile(
        "WAR_MUMAK",
        "War Mumak",
    )

    root_model = FieldedModel(
        id="WAR_MUMAK:1:1",
        configured_profile=ConfiguredProfile(
            profile=mumak,
        ),
    )

    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(
            FieldedModelStructureMember(
                profile_id="UNKNOWN_COMMANDER",
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="Unknown structure member Profile ID",
    ):
        build_fielded_model_structures(
            fielded_models=(root_model,),
            structure_definitions={
                "WAR_MUMAK": definition,
            },
            profiles_by_id={
                "WAR_MUMAK": mumak,
            },
        )

def test_structure_builder_links_same_warband_models():
    mumak = make_profile(
        "WAR_MUMAK",
        "War Mumak",
    )
    commander = make_profile(
        "COMMANDER",
        "Haradrim Commander",
    )
    warrior = make_profile(
        "HARADRIM_WARRIOR",
        "Haradrim Warrior",
    )

    root_model = FieldedModel(
        id="WAR_MUMAK:1:1",
        configured_profile=ConfiguredProfile(
            profile=mumak,
        ),
        warband_id="WARBAND_A",
    )

    warrior_model = FieldedModel(
        id="HARADRIM_WARRIOR:2:1",
        configured_profile=ConfiguredProfile(
            profile=warrior,
        ),
        warband_id="WARBAND_A",
    )

    commander_model = FieldedModel(
            id="COMMANDER:2:1",
            configured_profile=ConfiguredProfile(
                profile=commander,
            ),
            warband_id="WARBAND_A",
        )

    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(
            FieldedModelStructureMember(
                profile_id="COMMANDER",
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
        ),
        warband_member_relationship_type=(
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(
            root_model,
            commander_model,
            warrior_model,
        ),
        structure_definitions={
            "WAR_MUMAK": definition,
        },
        profiles_by_id={
            "WAR_MUMAK": mumak,
            "COMMANDER": commander,
            "HARADRIM_WARRIOR": warrior,
        },
    )

    howdah_relationships = tuple(
        relationship
        for relationship in result.relationships
        if relationship.relationship_type is (
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        )
    )

    assert len(howdah_relationships) == 1

    assert (
        howdah_relationships[0]
        .source_fielded_model_id
        == warrior_model.id
    )
    assert (
        howdah_relationships[0]
        .target_fielded_model_id
        == root_model.id
    )

def test_structure_builder_does_not_link_other_warband_models():
    mumak = make_profile(
        "WAR_MUMAK",
        "War Mumak",
    )
    commander = make_profile(
        "COMMANDER",
        "Haradrim Commander",
    )
    warrior = make_profile(
        "HARADRIM_WARRIOR",
        "Haradrim Warrior",
    )

    root_model = FieldedModel(
        id="WAR_MUMAK:1:1",
        configured_profile=ConfiguredProfile(
            profile=mumak,
        ),
        warband_id="WARBAND_A",
    )

    commander_model = FieldedModel(
            id="COMMANDER:2:1",
            configured_profile=ConfiguredProfile(
                profile=commander,
            ),
            warband_id="WARBAND_A",
        )

    other_warband_model = FieldedModel(
        id="HARADRIM_WARRIOR:2:1",
        configured_profile=ConfiguredProfile(
            profile=warrior,
        ),
        warband_id="WARBAND_B",
    )

    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(
            FieldedModelStructureMember(
                profile_id="COMMANDER",
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
        ),
        warband_member_relationship_type=(
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(
            root_model,
            commander_model,
            other_warband_model,
        ),
        structure_definitions={
            "WAR_MUMAK": definition,
        },
        profiles_by_id={
            "WAR_MUMAK": mumak,
            "COMMANDER": commander,
            "HARADRIM_WARRIOR": warrior,
        },
    )

    howdah_relationships = tuple(
        relationship
        for relationship in result.relationships
        if relationship.relationship_type is (
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        )
    )

    assert howdah_relationships == ()

def test_structure_builder_does_not_treat_commander_as_howdah_occupant():
    mumak = make_profile(
        "WAR_MUMAK",
        "War Mumak",
    )
    commander = make_profile(
        "COMMANDER",
        "Haradrim Commander",
    )

    root_model = FieldedModel(
        id="WAR_MUMAK:1:1",
        configured_profile=ConfiguredProfile(
            profile=mumak,
        ),
        warband_id="WARBAND_A",
    )

    commander_model = FieldedModel(
        id="COMMANDER:2:1",
        configured_profile=ConfiguredProfile(
            profile=commander,
        ),
        warband_id="WARBAND_A",
    )

    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(
            FieldedModelStructureMember(
                profile_id="COMMANDER",
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
        ),
        warband_member_relationship_type=(
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(
            root_model,
            commander_model,
        ),
        structure_definitions={
            "WAR_MUMAK": definition,
        },
        profiles_by_id={
            "WAR_MUMAK": mumak,
            "COMMANDER": commander,
        },
    )

    commander_relationships = tuple(
        relationship
        for relationship in result.relationships
        if relationship.relationship_type is (
            FieldedModelRelationshipType
            .WAR_BEAST_COMMANDER_OF
        )
    )

    howdah_relationships = tuple(
        relationship
        for relationship in result.relationships
        if relationship.relationship_type is (
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        )
    )

    assert len(commander_relationships) == 1
    assert howdah_relationships == ()

def test_mumak_registry_builds_commander_and_howdah_relationships():
    mumak = make_fielded_model(
        "WAR_MUMAK:1:1",
        "WAR_MUMAK",
        warband_id="WARBAND_A",
    )

    commander = make_fielded_model(
        "HARADRIM_COMMANDER:2:1",
        "HARADRIM_COMMANDER",
        warband_id="WARBAND_A",
    )

    warriors = tuple(
        make_fielded_model(
            f"HARADRIM_WARRIOR:3:{index}",
            "HARADRIM_WARRIOR",
            warband_id="WARBAND_A",
        )
        for index in range(1, 7)
    )

    result = build_fielded_model_structures(
        fielded_models=(
            mumak,
            commander,
            *warriors,
        ),
        structure_definitions=(
            FIELDED_MODEL_STRUCTURE_DEFINITIONS
        ),
        profiles_by_id={
            "WAR_MUMAK": (
                mumak.configured_profile.profile
            ),
            "HARADRIM_COMMANDER": (
                commander.configured_profile.profile
            ),
            "HARADRIM_WARRIOR": (
                warriors[0].configured_profile.profile
            ),
        },
    )

    assert len(result.fielded_models) == 8
    assert len(result.relationships) == 7

    commander_relationships = tuple(
        relationship
        for relationship in result.relationships
        if (
            relationship.relationship_type
            == FieldedModelRelationshipType
            .WAR_BEAST_COMMANDER_OF
        )
    )

    howdah_relationships = tuple(
        relationship
        for relationship in result.relationships
        if (
            relationship.relationship_type
            == FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        )
    )

    assert len(commander_relationships) == 1
    assert len(howdah_relationships) == 6

def test_structure_builder_links_repeated_same_profile_members():
    ballista = make_profile(
        "IRON_HILLS_BALLISTA",
        "Iron Hills Ballista",
    )
    siege_crew = make_profile(
        "IRON_HILLS_SIEGE_CREW",
        "Iron Hills Siege Crew",
    )

    root_model = FieldedModel(
        id="IRON_HILLS_BALLISTA:1:1",
        configured_profile=ConfiguredProfile(
            profile=ballista,
        ),
        warband_id="WARBAND_A",
    )

    crew_models = tuple(
        FieldedModel(
            id=f"IRON_HILLS_SIEGE_CREW:2:{index}",
            configured_profile=ConfiguredProfile(
                profile=siege_crew,
            ),
            warband_id="WARBAND_A",
        )
        for index in range(1, 5)
    )

    definition = FieldedModelStructureDefinition(
        root_profile_id="IRON_HILLS_BALLISTA",
        members=tuple(
            FieldedModelStructureMember(
                profile_id="IRON_HILLS_SIEGE_CREW",
                relationship_type=(
                    FieldedModelRelationshipType
                    .CREW_OF
                ),
            )
            for _ in range(4)
        ),
    )

    result = build_fielded_model_structures(
        fielded_models=(
            root_model,
            *crew_models,
        ),
        structure_definitions={
            "IRON_HILLS_BALLISTA": definition,
        },
        profiles_by_id={
            "IRON_HILLS_BALLISTA": ballista,
            "IRON_HILLS_SIEGE_CREW": siege_crew,
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
        root_model.id
    }

    assert {
        relationship.relationship_type
        for relationship in result.relationships
    } == {
        FieldedModelRelationshipType.CREW_OF
    }