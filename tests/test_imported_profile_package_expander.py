from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from imported_profile_package_definition import (
    ImportedProfilePackageDefinition,
)
from imported_profile_package_expander import (
    expand_imported_profile_package,
)
from imported_profile_package_member import (
    ImportedProfilePackageMember,
)


def test_expand_imported_profile_package_creates_peer_members():
    entry = ImportedConfiguredEntry(
        external_model_id="EXT_BARDS_FAMILY",
        quantity=1,
        warband_id="BARD_WARBAND",
    )

    definition = ImportedProfilePackageDefinition(
        external_model_id="EXT_BARDS_FAMILY",
        points=60,
        members=(
            ImportedProfilePackageMember(
                profile_id="BAIN",
            ),
            ImportedProfilePackageMember(
                profile_id="SIGRID",
            ),
            ImportedProfilePackageMember(
                profile_id="TILDA",
            ),
        ),
    )

    mapped = expand_imported_profile_package(
        entry,
        definition,
    )

    assert tuple(
        member.profile_id
        for member in mapped
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )

    assert all(
        member.quantity == 1
        for member in mapped
    )

    assert all(
        member.warband_id == "BARD_WARBAND"
        for member in mapped
    )