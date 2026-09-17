from army_list import ArmyList
from faction import Faction
from profiles import Profile
from army_builder import build_army_from_definition
from army_definition import ArmyDefinition, ArmyEntryDefinition

def make_thrain() -> Profile:
    return Profile(
        id="THRAIN_THE_BROKEN",
        name="Thráin the Broken",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=2,
        defence=4,
        attacks=1,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=1,
        max_in_army=1,
        races={"DWARF"},
    )


def test_same_thrain_profile_can_exist_in_different_army_list_contexts():
    thrain = make_thrain()

    erebor = Faction(
        id="EREBOR",
        name="Erebor",
    )

    white_council = ArmyList(
        id="THE_WHITE_COUNCIL",
        name="The White Council",
        faction=erebor,
        profiles=[thrain],
    )

    pits_of_dol_guldur = ArmyList(
        id="PITS_OF_DOL_GULDUR",
        name="Pits of Dol Guldur",
        faction=erebor,
        profiles=[thrain],
    )

    assert white_council.profiles[0] is thrain
    assert pits_of_dol_guldur.profiles[0] is thrain

    assert white_council.profiles[0] is pits_of_dol_guldur.profiles[0]

    assert thrain.id == "THRAIN_THE_BROKEN"
    assert thrain.races == {"DWARF"}

def test_thrain_context_can_be_distinguished_by_army_list_identity():
    thrain = make_thrain()

    erebor = Faction(
        id="EREBOR",
        name="Erebor",
    )

    white_council = ArmyList(
        id="THE_WHITE_COUNCIL",
        name="The White Council",
        faction=erebor,
        profiles=[thrain],
    )

    pits_of_dol_guldur = ArmyList(
        id="PITS_OF_DOL_GULDUR",
        name="Pits of Dol Guldur",
        faction=erebor,
        profiles=[thrain],
    )

    assert white_council.id == "THE_WHITE_COUNCIL"
    assert pits_of_dol_guldur.id == "PITS_OF_DOL_GULDUR"

    assert thrain.id == "THRAIN_THE_BROKEN"
    assert not hasattr(thrain, "alignment")

def test_army_builder_keeps_thrain_profile_identity_separate_from_list_context():
    thrain = make_thrain()

    erebor = Faction(
        id="EREBOR",
        name="Erebor",
    )

    white_council = ArmyList(
        id="THE_WHITE_COUNCIL",
        name="The White Council",
        faction=erebor,
        profiles=[thrain],
    )

    pits_of_dol_guldur = ArmyList(
        id="PITS_OF_DOL_GULDUR",
        name="Pits of Dol Guldur",
        faction=erebor,
        profiles=[thrain],
    )

    army_lists_by_id = {
        white_council.id: white_council,
        pits_of_dol_guldur.id: pits_of_dol_guldur,
    }

    profiles_by_id = {
        thrain.id: thrain,
    }

    white_council_definition = ArmyDefinition(
        id="WHITE_COUNCIL_TEST",
        name="White Council test",
        army_list_id=white_council.id,
        points_limit=100,
        entries=[
            ArmyEntryDefinition(
                profile_id=thrain.id,
            ),
        ],
    )

    pits_definition = ArmyDefinition(
        id="PITS_TEST",
        name="Pits test",
        army_list_id=pits_of_dol_guldur.id,
        points_limit=100,
        entries=[
            ArmyEntryDefinition(
                profile_id=thrain.id,
            ),
        ],
    )

    white_council_army, resolved_white_council = (
        build_army_from_definition(
            white_council_definition,
            profiles_by_id,
            army_lists_by_id,
        )
    )

    pits_army, resolved_pits = build_army_from_definition(
        pits_definition,
        profiles_by_id,
        army_lists_by_id,
    )

    assert white_council_army.entries[0].profile is thrain
    assert pits_army.entries[0].profile is thrain

    assert resolved_white_council is white_council
    assert resolved_pits is pits_of_dol_guldur