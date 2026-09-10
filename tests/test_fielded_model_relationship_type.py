from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


def test_fielded_model_relationship_types_have_expected_values():
    assert (
        FieldedModelRelationshipType.PASSENGER_OF.value
        == "PASSENGER_OF"
    )

    assert (
        FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF.value
        == "WAR_BEAST_COMMANDER_OF"
    )

    assert (
        FieldedModelRelationshipType.HOWDAH_OCCUPANT_OF.value
        == "HOWDAH_OCCUPANT_OF"
    )