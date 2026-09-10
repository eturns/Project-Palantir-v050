from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_builder import (
    build_fielded_model_relationship_set,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from profiles import Profile


def make_fielded_model(
    fielded_model_id: str,
) -> FieldedModel:
    profile = Profile(
        id=fielded_model_id.split(":")[0],
        name=fielded_model_id,
        points=1,
        movement=6,
        fight=1,
        shooting="6+",
        strength=1,
        defence=1,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    return FieldedModel(
        id=fielded_model_id,
        configured_profile=ConfiguredProfile(
            profile=profile,
        ),
    )


def test_builder_creates_relationship_set():
    gimli = make_fielded_model("GIMLI:1:1")
    legolas = make_fielded_model("LEGOLAS:1:1")

    relationship = FieldedModelRelationship(
        source_fielded_model_id=gimli.id,
        target_fielded_model_id=legolas.id,
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    relationship_set = (
        build_fielded_model_relationship_set(
            fielded_models=(
                gimli,
                legolas,
            ),
            relationships=(
                relationship,
            ),
        )
    )

    assert relationship_set.fielded_models == (
        gimli,
        legolas,
    )

    assert relationship_set.relationships == (
        relationship,
    )


def test_builder_defaults_to_no_relationships():
    gimli = make_fielded_model("GIMLI:1:1")

    relationship_set = (
        build_fielded_model_relationship_set(
            fielded_models=(gimli,),
        )
    )

    assert relationship_set.fielded_models == (
        gimli,
    )

    assert relationship_set.relationships == ()