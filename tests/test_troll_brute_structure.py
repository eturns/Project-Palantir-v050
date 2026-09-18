from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_relationship import FieldedModelRelationship
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from profiles import Profile


def make_profile(
    profile_id: str,
    name: str,
    max_in_army: int = 0,
) -> Profile:
    return Profile(
        id=profile_id,
        name=name,
        points=0,
        movement=6,
        fight=5,
        shooting="6+",
        strength=5,
        defence=6,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=max_in_army,
    )


def test_troll_brute_can_be_represented_as_two_related_fielded_models():
    troll_profile = make_profile(
        "TROLL_BRUTE",
        "Troll Brute",
    )
    commander_profile = make_profile(
        "ORC_COMMANDER",
        "Orc Commander",
    )

    troll = FieldedModel(
        id="TROLL_BRUTE:1",
        configured_profile=ConfiguredProfile(
            profile=troll_profile,
        ),
    )

    commander = FieldedModel(
        id="TROLL_BRUTE:1:COMMANDER",
        configured_profile=ConfiguredProfile(
            profile=commander_profile,
        ),
    )

    relationship = FieldedModelRelationship(
        source_fielded_model_id=commander.id,
        target_fielded_model_id=troll.id,
        relationship_type=(
            FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF
        ),
    )

    assert troll.profile_id == "TROLL_BRUTE"
    assert commander.profile_id == "ORC_COMMANDER"

    assert relationship.source_fielded_model_id == commander.id
    assert relationship.target_fielded_model_id == troll.id
    assert (
        relationship.relationship_type
        == FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF
    )

from army_purchase_definition import ArmyPurchaseDefinition


def test_troll_brute_purchase_represents_one_package_for_two_entities():
    purchase = ArmyPurchaseDefinition(
        id="[army-of-gundabad] troll-brute",
        points=120,
        quantity=1,
        warband_id="TROLL_BRUTE_WARBAND",
    )

    assert purchase.total_points() == 120
    assert purchase.quantity == 1
    assert purchase.warband_id == "TROLL_BRUTE_WARBAND"

def test_bofur_can_replace_orc_commander_as_troll_brute_commander():
    troll_profile = make_profile(
        "TROLL_BRUTE",
        "Troll Brute",
    )
    bofur_profile = make_profile(
        "BOFUR_CHAMPION_OF_EREBOR",
        "Bofur the Dwarf, Champion of Erebor",
    )

    troll = FieldedModel(
        id="BOFUR_TROLL_BRUTE:1",
        configured_profile=ConfiguredProfile(
            profile=troll_profile,
        ),
    )

    bofur = FieldedModel(
        id="BOFUR_TROLL_BRUTE:1:BOFUR",
        configured_profile=ConfiguredProfile(
            profile=bofur_profile,
        ),
    )

    relationship = FieldedModelRelationship(
        source_fielded_model_id=bofur.id,
        target_fielded_model_id=troll.id,
        relationship_type=(
            FieldedModelRelationshipType
            .WAR_BEAST_COMMANDER_OF
        ),
    )

    assert relationship.source_fielded_model_id == bofur.id
    assert relationship.target_fielded_model_id == troll.id
    assert (
        relationship.relationship_type
        == FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )