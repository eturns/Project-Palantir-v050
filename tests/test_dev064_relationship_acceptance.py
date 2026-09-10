from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from profiles import Profile
from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_set import (
    FieldedModelRelationshipSet,
)
from army import Army

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

def test_dev064_passenger_relationship_preserves_distinct_models():
    relationship = FieldedModelRelationship(
        source_fielded_model_id="GIMLI:1:1",
        target_fielded_model_id="LEGOLAS:1:1",
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    assert relationship.source_fielded_model_id != (
        relationship.target_fielded_model_id
    )


def test_dev064_war_beast_commander_relationship_is_distinct_from_passenger():
    relationship = FieldedModelRelationship(
        source_fielded_model_id="HARADRIM_COMMANDER:1:1",
        target_fielded_model_id="WAR_MUMAK:1:1",
        relationship_type=(
            FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF
        ),
    )

    assert relationship.relationship_type is not (
        FieldedModelRelationshipType.PASSENGER_OF
    )


def test_dev064_howdah_occupant_relationship_is_distinct_from_passenger():
    relationship = FieldedModelRelationship(
        source_fielded_model_id="HARADRIM_WARRIOR:1:1",
        target_fielded_model_id="WAR_MUMAK:1:1",
        relationship_type=(
            FieldedModelRelationshipType.HOWDAH_OCCUPANT_OF
        ),
    )

    assert relationship.relationship_type is not (
        FieldedModelRelationshipType.PASSENGER_OF
    )

def test_dev064_passenger_remains_separate_fielded_model():
    carrier = FieldedModel(
        id="CARRIER:1:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "CARRIER",
                "Carrier",
            ),
        ),
    )

    passenger = FieldedModel(
        id="PASSENGER:2:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "PASSENGER",
                "Passenger",
            ),
        ),
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

    assert len(
        relationship_set.fielded_models
    ) == 2

    assert (
        relationship.source_fielded_model_id
        != relationship.target_fielded_model_id
    )


def test_dev064_chariot_remains_single_fielded_model():
    chariot = FieldedModel(
        id="CHARIOT:1:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "CHARIOT",
                "Chariot",
            ),
        ),
    )

    relationship_set = FieldedModelRelationshipSet(
        fielded_models=(chariot,),
        relationships=(),
    )

    assert len(
        relationship_set.fielded_models
    ) == 1

    assert relationship_set.relationships == ()

def test_dev064_relationships_do_not_reduce_rules_model_count():
    carrier = FieldedModel(
        id="CARRIER:1:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "CARRIER",
                "Carrier",
            ),
        ),
    )

    passenger = FieldedModel(
        id="PASSENGER:2:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "PASSENGER",
                "Passenger",
            ),
        ),
    )

    relationship_set = FieldedModelRelationshipSet(
        fielded_models=(
            carrier,
            passenger,
        ),
        relationships=(
            FieldedModelRelationship(
                source_fielded_model_id=(
                    passenger.id
                ),
                target_fielded_model_id=(
                    carrier.id
                ),
                relationship_type=(
                    FieldedModelRelationshipType
                    .PASSENGER_OF
                ),
            ),
        ),
    )

    assert len(
        relationship_set.fielded_models
    ) == 2

def test_dev064_war_beast_structure_preserves_eight_rules_models():
    mumak = FieldedModel(
        id="WAR_MUMAK:1:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "WAR_MUMAK",
                "War Mumak",
            ),
        ),
        warband_id="WARBAND_A",
    )

    commander = FieldedModel(
        id="HARADRIM_COMMANDER:2:1",
        configured_profile=ConfiguredProfile(
            profile=make_profile(
                "HARADRIM_COMMANDER",
                "Haradrim Commander",
            ),
        ),
        warband_id="WARBAND_A",
    )

    warriors = tuple(
        FieldedModel(
            id=f"HARADRIM_WARRIOR:3:{index}",
            configured_profile=ConfiguredProfile(
                profile=make_profile(
                    "HARADRIM_WARRIOR",
                    "Haradrim Warrior",
                ),
            ),
            warband_id="WARBAND_A",
        )
        for index in range(1, 7)
    )

    relationship_set = FieldedModelRelationshipSet(
        fielded_models=(
            mumak,
            commander,
            *warriors,
        ),
        relationships=(
            FieldedModelRelationship(
                source_fielded_model_id=commander.id,
                target_fielded_model_id=mumak.id,
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
            *tuple(
                FieldedModelRelationship(
                    source_fielded_model_id=warrior.id,
                    target_fielded_model_id=mumak.id,
                    relationship_type=(
                        FieldedModelRelationshipType
                        .HOWDAH_OCCUPANT_OF
                    ),
                )
                for warrior in warriors
            ),
        ),
    )

    assert len(
        relationship_set.fielded_models
    ) == 8

    assert len(
        relationship_set.relationships
    ) == 7

def test_dev064_war_beast_army_model_count_is_eight():
    army = Army()

    army.add_configured_profile(
        ConfiguredProfile(
            profile=make_profile(
                "WAR_MUMAK",
                "War Mumak",
            ),
        ),
        quantity=1,
        warband_id="WARBAND_A",
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=make_profile(
                "HARADRIM_COMMANDER",
                "Haradrim Commander",
            ),
        ),
        quantity=1,
        warband_id="WARBAND_A",
    )

    army.add_configured_profile(
        ConfiguredProfile(
            profile=make_profile(
                "HARADRIM_WARRIOR",
                "Haradrim Warrior",
            ),
        ),
        quantity=6,
        warband_id="WARBAND_A",
    )

    assert army.model_count() == 8
    assert len(army.fielded_models()) == 8