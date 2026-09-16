from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from imported_profile_package_definition import (
    ImportedProfilePackageDefinition,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)


def expand_imported_profile_package(
    entry: ImportedConfiguredEntry,
    definition: ImportedProfilePackageDefinition,
) -> list[MappedConfiguredEntry]:
    return [
        MappedConfiguredEntry(
            profile_id=member.profile_id,
            external_option_ids=member.option_ids,
            quantity=entry.quantity,
            warband_id=entry.warband_id,
        )
        for member in definition.members
    ]