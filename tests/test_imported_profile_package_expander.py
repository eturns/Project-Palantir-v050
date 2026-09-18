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
from importers.mesbg_list_builder_profile_package_map import (
    IMPORTED_PROFILE_PACKAGE_DEFINITIONS,
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

def test_troll_brute_package_expands_to_troll_and_commander():
    entry = ImportedConfiguredEntry(
        external_model_id="[army-of-gundabad] troll-brute",
        quantity=1,
        warband_id="TROLL_BRUTE_WARBAND",
    )

    definition = IMPORTED_PROFILE_PACKAGE_DEFINITIONS[
        "[army-of-gundabad] troll-brute"
    ]

    mapped = expand_imported_profile_package(
        entry=entry,
        definition=definition,
    )

    assert tuple(
        member.profile_id
        for member in mapped
    ) == (
        "TROLL_BRUTE",
        "ORC_COMMANDER",
    )

    assert tuple(
        member.warband_id
        for member in mapped
    ) == (
        "TROLL_BRUTE_WARBAND",
        "TROLL_BRUTE_WARBAND",
    )