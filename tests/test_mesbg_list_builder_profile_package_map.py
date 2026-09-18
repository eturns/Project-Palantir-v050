from importers.mesbg_list_builder_profile_package_map import (
    IMPORTED_PROFILE_PACKAGE_DEFINITIONS,
)
from imported_profile_package_definition import (
    ImportedProfilePackageDefinition,
)
from imported_profile_package_member import (
    ImportedProfilePackageMember,
)


def test_bards_family_package_definition_is_registered():
    definition = IMPORTED_PROFILE_PACKAGE_DEFINITIONS[
        "[army-of-lake-town] bard's-family"
    ]

    assert definition.points == 60

    assert tuple(
        member.profile_id
        for member in definition.members
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )

def test_troll_brute_package_definition_is_registered():
    definition = IMPORTED_PROFILE_PACKAGE_DEFINITIONS[
        "[army-of-gundabad] troll-brute"
    ]

    assert definition.points == 120

    assert tuple(
        member.profile_id
        for member in definition.members
    ) == (
        "TROLL_BRUTE",
        "ORC_COMMANDER",
    )