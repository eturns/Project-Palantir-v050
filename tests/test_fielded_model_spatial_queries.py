from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_set import (
    FieldedModelRelationshipSet,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_spatial_queries import (
    spatial_relationships,
)
from profiles import Profile


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
) -> FieldedModel:
    return FieldedModel(
        id=fielded_model_id,
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                profile_id,
            ),
        ),
    )


def test_spatial_relationships_returns_linked_relationships():
    carrier = make_fielded_model(
        "CARRIER:1:1",
        "CARRIER",
    )
    passenger = make_fielded_model(
        "PASSENGER:2:1",
        "PASSENGER",
    )

    relationship = FieldedModelRelationship(
        source_fielded_model_id=passenger.id,
        target_fielded_model_id=carrier.id,
        relationship_type=(
            FieldedModelRelationshipType
            .PASSENGER_OF
        ),
    )

    relationship_set = FieldedModelRelationshipSet(
        fielded_models=(
            carrier,
            passenger,
        ),
        relationships=(relationship,),
    )

    assert spatial_relationships(
        relationship_set
    ) == (relationship,)


def test_spatial_relationships_handles_empty_set():
    model = make_fielded_model(
        "MODEL:1:1",
        "MODEL",
    )

    relationship_set = FieldedModelRelationshipSet(
        fielded_models=(model,),
        relationships=(),
    )

    assert spatial_relationships(
        relationship_set
    ) == ()