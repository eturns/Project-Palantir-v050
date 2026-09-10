from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_definition import (
    FieldedModelStructureDefinition,
)
from fielded_model_structure_member import (
    FieldedModelStructureMember,
)
from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
)


IMPORTED_FIELDED_STRUCTURE_DEFINITIONS = {
    "[usurpers-of-edoras] war-mumak-of-harad": (
        ImportedFieldedStructureDefinition(
            external_model_id=(
                "[usurpers-of-edoras] "
                "war-mumak-of-harad"
            ),
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )
    ),
}


FIELDED_MODEL_STRUCTURE_DEFINITIONS = {
    "WAR_MUMAK": (
        FieldedModelStructureDefinition(
            root_profile_id="WAR_MUMAK",
            members=(
                FieldedModelStructureMember(
                    profile_id=(
                        "HARADRIM_COMMANDER"
                    ),
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
    ),
}