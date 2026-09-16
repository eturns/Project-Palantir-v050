from importers.mesbg_list_builder_profile_package_map import (
    IMPORTED_PROFILE_PACKAGE_DEFINITIONS,
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