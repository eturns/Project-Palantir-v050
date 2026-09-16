from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)


def expand_imported_fielded_structure(
    entry: ImportedConfiguredEntry,
    definition: ImportedFieldedStructureDefinition,
) -> list[MappedConfiguredEntry]:
    expanded_entries = [
        MappedConfiguredEntry(
            profile_id=definition.root_profile_id,
            external_option_ids=(
                entry.external_option_ids
            ),
            quantity=entry.quantity,
            warband_id=entry.warband_id,
        )
    ]

    if definition.members:
        for member in definition.members:
            expanded_entries.append(
                MappedConfiguredEntry(
                    profile_id=member.profile_id,
                    external_option_ids=(
                        member.option_ids
                    ),
                    quantity=entry.quantity,
                    warband_id=entry.warband_id,
                )
            )
    else:
        for member_profile_id in (
            definition.member_profile_ids
        ):
            expanded_entries.append(
                MappedConfiguredEntry(
                    profile_id=member_profile_id,
                    quantity=entry.quantity,
                    warband_id=entry.warband_id,
                )
            )

    return expanded_entries