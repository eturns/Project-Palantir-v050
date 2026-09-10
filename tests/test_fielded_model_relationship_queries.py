from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_queries import (
    get_relationships_from_source,
    get_relationships_of_type,
    get_relationships_to_target,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


def make_relationship(
    *,
    source: str,
    target: str,
    relationship_type: FieldedModelRelationshipType,
) -> FieldedModelRelationship:
    return FieldedModelRelationship(
        source_fielded_model_id=source,
        target_fielded_model_id=target,
        relationship_type=relationship_type,
    )


def test_get_relationships_from_source():
    passenger = make_relationship(
        source="GIMLI:1:1",
        target="LEGOLAS:1:1",
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    howdah_occupant = make_relationship(
        source="HARADRIM:1:1",
        target="WAR_MUMAK:1:1",
        relationship_type=(
            FieldedModelRelationshipType.HOWDAH_OCCUPANT_OF
        ),
    )

    relationships = (
        passenger,
        howdah_occupant,
    )

    assert get_relationships_from_source(
        relationships,
        "GIMLI:1:1",
    ) == (
        passenger,
    )


def test_get_relationships_to_target():
    first = make_relationship(
        source="HARADRIM:1:1",
        target="WAR_MUMAK:1:1",
        relationship_type=(
            FieldedModelRelationshipType.HOWDAH_OCCUPANT_OF
        ),
    )

    second = make_relationship(
        source="HARADRIM:1:2",
        target="WAR_MUMAK:1:1",
        relationship_type=(
            FieldedModelRelationshipType.HOWDAH_OCCUPANT_OF
        ),
    )

    relationships = (
        first,
        second,
    )

    assert get_relationships_to_target(
        relationships,
        "WAR_MUMAK:1:1",
    ) == (
        first,
        second,
    )


def test_get_relationships_of_type():
    passenger = make_relationship(
        source="GIMLI:1:1",
        target="LEGOLAS:1:1",
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    commander = make_relationship(
        source="HARADRIM_COMMANDER:1:1",
        target="WAR_MUMAK:1:1",
        relationship_type=(
            FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF
        ),
    )

    relationships = (
        passenger,
        commander,
    )

    assert get_relationships_of_type(
        relationships,
        FieldedModelRelationshipType.PASSENGER_OF,
    ) == (
        passenger,
    )