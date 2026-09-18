from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from importers.mesbg_list_builder_fielded_structure_map import (
    FIELDED_MODEL_STRUCTURE_DEFINITIONS,
    IMPORTED_FIELDED_STRUCTURE_DEFINITIONS,
)
from fielded_model import FieldedModel
from fielded_model_structure_builder import (
    build_fielded_model_structures,
)
from profiles import Profile
from configured_profile import ConfiguredProfile
from profile_option import ProfileOption
from profile_option_profile_assignment import (
    ProfileOptionProfileAssignment,
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
        max_in_army=0,
    )

def test_mumak_import_structure_definition_exists():
    definition = (
        IMPORTED_FIELDED_STRUCTURE_DEFINITIONS[
            "[usurpers-of-edoras] war-mumak-of-harad"
        ]
    )

    assert definition.root_profile_id == "WAR_MUMAK"

    assert definition.member_profile_ids == (
        "HARADRIM_COMMANDER",
    )


def test_mumak_fielded_structure_definition_exists():
    definition = (
        FIELDED_MODEL_STRUCTURE_DEFINITIONS[
            "WAR_MUMAK"
        ]
    )

    assert (
        definition.members[0].profile_id
        == "HARADRIM_COMMANDER"
    )

    assert (
        definition.members[0].relationship_type
        == FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )

    assert (
        definition.warband_member_relationship_type
        == FieldedModelRelationshipType
        .HOWDAH_OCCUPANT_OF
    )

def test_troll_brute_fielded_structure_definition_exists():
    definition = (
        FIELDED_MODEL_STRUCTURE_DEFINITIONS[
            "TROLL_BRUTE"
        ]
    )

    assert definition.root_profile_id == "TROLL_BRUTE"

    assert len(definition.members) == 1

    assert (
        definition.members[0].profile_id
        == "ORC_COMMANDER"
    )

    assert (
        definition.members[0].relationship_type
        == FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )

    assert (
        definition.warband_member_relationship_type
        is None
    )

def test_bofur_troll_brute_structure_does_not_require_orc_commander():
    troll_profile = make_profile(
        "TROLL_BRUTE",
        "Troll Brute",
    )

    bofur_profile = make_profile(
        "BOFUR_CHAMPION_OF_EREBOR",
        "Bofur the Dwarf, Champion of Erebor",
    )

    bofur_troll_brute_option = ProfileOption(
        id="BOFUR_TROLL_BRUTE",
        name="Troll Brute",
        points=100,
        profile_assignments=(
            ProfileOptionProfileAssignment(
                profile_id="TROLL_BRUTE",
                relationship_type=(
                    FieldedModelRelationshipType
                    .WAR_BEAST_COMMANDER_OF
                ),
            ),
        ),
    )

    bofur_profile.profile_options.append(
        bofur_troll_brute_option
    )

    troll_brute = FieldedModel(
        id="TROLL_BRUTE_1",
        configured_profile=ConfiguredProfile(
            profile=troll_profile,
        ),
        warband_id="WARBAND_A",
    )

    bofur = FieldedModel(
        id="BOFUR_1",
        configured_profile=ConfiguredProfile(
            profile=bofur_profile,
            selected_options=(
                bofur_troll_brute_option,
            ),
        ),
        warband_id="WARBAND_A",
    )

    relationships = build_fielded_model_structures(
        fielded_models=(
            troll_brute,
            bofur,
        ),
        structure_definitions=(
            FIELDED_MODEL_STRUCTURE_DEFINITIONS
        ),
        profiles_by_id={
            "TROLL_BRUTE": troll_profile,
            "BOFUR_CHAMPION_OF_EREBOR": bofur_profile,
            "ORC_COMMANDER": make_profile(
                "ORC_COMMANDER",
                "Orc Commander",
            ),
        },
    )

    assert len(relationships.relationships) == 1

    relationship = relationships.relationships[0]

    assert relationship.source_fielded_model_id == "BOFUR_1"
    assert relationship.target_fielded_model_id == "TROLL_BRUTE_1"
    assert (
        relationship.relationship_type
        is FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF
    )