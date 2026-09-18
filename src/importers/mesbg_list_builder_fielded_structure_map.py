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
from imported_fielded_structure_member import (
    ImportedFieldedStructureMember,
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
    "[the-iron-hills] iron-hills-ballista": (
        ImportedFieldedStructureDefinition(
            external_model_id=(
                "[the-iron-hills] "
                "iron-hills-ballista"
            ),
            root_profile_id="IH_BALLISTA",
            members=(
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                    option_ids=(
                        "SIEGE_VETERAN",
                    ),
                ),
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
    "IH_BALLISTA": (
        FieldedModelStructureDefinition(
            root_profile_id="IH_BALLISTA",
            members=tuple(
                FieldedModelStructureMember(
                    profile_id="IH_SIEGE_CREW",
                    relationship_type=(
                        FieldedModelRelationshipType
                        .CREW_OF
                    ),
                )
                for _ in range(4)
            ),
        )
    ),
    "TROLL_BRUTE": (
        FieldedModelStructureDefinition(
            root_profile_id="TROLL_BRUTE",
            members=(
                FieldedModelStructureMember(
                    profile_id="ORC_COMMANDER",
                    relationship_type=(
                        FieldedModelRelationshipType
                        .WAR_BEAST_COMMANDER_OF
                    ),
                ),
            ),
        )
    ),
}