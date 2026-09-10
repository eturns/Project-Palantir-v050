import pytest

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


def test_relationship_set_preserves_models_and_relationships():
    gimli = make_fielded_model("GIMLI:1:1")
    legolas = make_fielded_model("LEGOLAS:1:1")

    relationship = FieldedModelRelationship(
        source_fielded_model_id=gimli.id,
        target_fielded_model_id=legolas.id,
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    relationship_set = FieldedModelRelationshipSet(
        fielded_models=(gimli, legolas),
        relationships=(relationship,),
    )

    assert relationship_set.fielded_models == (
        gimli,
        legolas,
    )

    assert relationship_set.relationships == (
        relationship,
    )


def test_relationship_set_rejects_duplicate_model_ids():
    first = make_fielded_model("GIMLI:1:1")
    second = make_fielded_model("GIMLI:1:1")

    with pytest.raises(
        ValueError,
        match="FieldedModel ids must be unique.",
    ):
        FieldedModelRelationshipSet(
            fielded_models=(first, second),
            relationships=(),
        )


def test_relationship_set_rejects_missing_source_model():
    legolas = make_fielded_model("LEGOLAS:1:1")

    relationship = FieldedModelRelationship(
        source_fielded_model_id="GIMLI:1:1",
        target_fielded_model_id=legolas.id,
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Relationship source must belong to "
            "the fielded model set."
        ),
    ):
        FieldedModelRelationshipSet(
            fielded_models=(legolas,),
            relationships=(relationship,),
        )


def test_relationship_set_rejects_missing_target_model():
    gimli = make_fielded_model("GIMLI:1:1")

    relationship = FieldedModelRelationship(
        source_fielded_model_id=gimli.id,
        target_fielded_model_id="LEGOLAS:1:1",
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Relationship target must belong to "
            "the fielded model set."
        ),
    ):
        FieldedModelRelationshipSet(
            fielded_models=(gimli,),
            relationships=(relationship,),
        )


def test_relationship_set_rejects_duplicate_relationships():
    gimli = make_fielded_model("GIMLI:1:1")
    legolas = make_fielded_model("LEGOLAS:1:1")

    relationship = FieldedModelRelationship(
        source_fielded_model_id=gimli.id,
        target_fielded_model_id=legolas.id,
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Duplicate fielded model relationships "
            "are not permitted."
        ),
    ):
        FieldedModelRelationshipSet(
            fielded_models=(gimli, legolas),
            relationships=(
                relationship,
                relationship,
            ),
        )