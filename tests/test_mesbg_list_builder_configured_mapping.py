from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from importers.mesbg_list_builder_json_importer import (
    map_imported_configured_entries,
    group_mapped_configured_entries,
    get_imported_configured_entries,
)
from importers.mesbg_list_builder_profile_id_map import (
    EXTERNAL_PROFILE_IDS,
)
from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
)
from imported_fielded_structure_member import (
    ImportedFieldedStructureMember,
)
from imported_profile_package_definition import (
    ImportedProfilePackageDefinition,
)
from imported_profile_package_member import (
    ImportedProfilePackageMember,
)

def get_known_external_model_id() -> str:
    return next(
        iter(EXTERNAL_PROFILE_IDS)
    )


def test_map_imported_configured_entry():
    external_model_id = (
        get_known_external_model_id()
    )

    entry = ImportedConfiguredEntry(
        external_model_id=external_model_id,
        external_option_ids=("OPT_TEST",),
        quantity=2,
    )

    mapped_entries = (
        map_imported_configured_entries(
            [entry]
        )
    )

    assert len(mapped_entries) == 1

    assert mapped_entries[0].profile_id == (
        EXTERNAL_PROFILE_IDS[
            external_model_id
        ]
    )

    assert mapped_entries[0].external_option_ids == (
        "OPT_TEST",
    )

    assert mapped_entries[0].quantity == 2


def test_map_imported_configured_entries_preserves_distinct_options():
    external_model_id = (
        get_known_external_model_id()
    )

    entries = [
        ImportedConfiguredEntry(
            external_model_id=external_model_id,
            external_option_ids=("OPT_A",),
            quantity=3,
        ),
        ImportedConfiguredEntry(
            external_model_id=external_model_id,
            external_option_ids=("OPT_B",),
            quantity=2,
        ),
    ]

    mapped_entries = (
        map_imported_configured_entries(
            entries
        )
    )

    assert len(mapped_entries) == 2

    assert mapped_entries[0].external_option_ids == (
        "OPT_A",
    )
    assert mapped_entries[0].quantity == 3

    assert mapped_entries[1].external_option_ids == (
        "OPT_B",
    )
    assert mapped_entries[1].quantity == 2


def test_map_imported_configured_entries_rejects_unknown_model_id():
    entry = ImportedConfiguredEntry(
        external_model_id="UNKNOWN_MODEL",
    )

    try:
        map_imported_configured_entries(
            [entry]
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "external model ID."
        )


def test_map_imported_configured_entries_handles_empty_list():
    assert map_imported_configured_entries(
        []
    ) == []

def test_map_imported_configured_entries_preserves_warband_id():
    external_model_id = (
        get_known_external_model_id()
    )

    entry = ImportedConfiguredEntry(
        external_model_id=external_model_id,
        external_option_ids=("OPT_TEST",),
        quantity=2,
        warband_id="WARBAND_A",
    )

    mapped_entries = (
        map_imported_configured_entries(
            [entry]
        )
    )

    assert len(mapped_entries) == 1
    assert mapped_entries[0].warband_id == (
        "WARBAND_A"
    )

def test_map_imported_configured_entries_expands_structure():
    entries = [
        ImportedConfiguredEntry(
            external_model_id="EXT_MUMAK",
            quantity=1,
            warband_id="WARBAND_A",
        )
    ]

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )
    )

    mapped_entries = map_imported_configured_entries(
        entries,
        structure_definitions={
            "EXT_MUMAK": structure_definition,
        },
    )

    assert len(mapped_entries) == 2

    assert mapped_entries[0].profile_id == (
        "WAR_MUMAK"
    )
    assert mapped_entries[0].warband_id == (
        "WARBAND_A"
    )

    assert mapped_entries[1].profile_id == (
        "HARADRIM_COMMANDER"
    )
    assert mapped_entries[1].warband_id == (
        "WARBAND_A"
    )

def test_map_imported_structure_preserves_member_specific_options():
    entries = [
        ImportedConfiguredEntry(
            external_model_id="EXT_BALLISTA",
            quantity=1,
            warband_id="WARBAND_A",
        )
    ]

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_BALLISTA",
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
                    option_ids=("SIEGE_VETERAN",),
                ),
            ),
        )
    )

    mapped_entries = map_imported_configured_entries(
        entries,
        structure_definitions={
            "EXT_BALLISTA": structure_definition,
        },
    )

    assert len(mapped_entries) == 5

    assert mapped_entries[4].profile_id == (
        "IH_SIEGE_CREW"
    )

    assert mapped_entries[4].external_option_ids == (
        "SIEGE_VETERAN",
    )

def test_ballista_structure_groups_three_crew_and_one_veteran():
    entries = [
        ImportedConfiguredEntry(
            external_model_id="EXT_BALLISTA",
            quantity=1,
            warband_id="WARBAND_A",
        )
    ]

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_BALLISTA",
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
                    option_ids=("SIEGE_VETERAN",),
                ),
            ),
        )
    )

    mapped_entries = map_imported_configured_entries(
        entries,
        structure_definitions={
            "EXT_BALLISTA": structure_definition,
        },
    )

    grouped_entries = group_mapped_configured_entries(
        mapped_entries
    )

    assert len(grouped_entries) == 3

    assert grouped_entries[0].profile_id == (
        "IH_BALLISTA"
    )
    assert grouped_entries[0].quantity == 1

    assert grouped_entries[1].profile_id == (
        "IH_SIEGE_CREW"
    )
    assert grouped_entries[1].external_option_ids == ()
    assert grouped_entries[1].quantity == 3

    assert grouped_entries[2].profile_id == (
        "IH_SIEGE_CREW"
    )
    assert grouped_entries[2].external_option_ids == (
        "SIEGE_VETERAN",
    )
    assert grouped_entries[2].quantity == 1

def test_map_imported_package_expands_to_peer_profiles():
    entries = [
        ImportedConfiguredEntry(
            external_model_id=(
                "[army-of-lake-town] bard's-family"
            ),
            quantity=1,
            warband_id="BARD_WARBAND",
        )
    ]

    package_definition = (
        ImportedProfilePackageDefinition(
            external_model_id=(
                "[army-of-lake-town] bard's-family"
            ),
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
    )

    mapped = map_imported_configured_entries(
        entries,
        structure_definitions={},
        package_definitions={
            (
                "[army-of-lake-town] "
                "bard's-family"
            ): package_definition,
        },
    )

    assert tuple(
        entry.profile_id
        for entry in mapped
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )

    assert all(
        entry.warband_id == "BARD_WARBAND"
        for entry in mapped
    )

def test_bards_family_export_shape_maps_to_three_peer_profiles():
    data = {
        "warbands": [
            {
                "id": "BARD_WARBAND",
                "units": [
                    {
                        "model_id": (
                            "[army-of-lake-town] bard's-family"
                        ),
                        "MWFW": [
                            [
                                "Bain, Son of Bard",
                                "1:3:2:2",
                            ],
                            [
                                "Sigrid",
                                "0:1:2:1",
                            ],
                            [
                                "Tilda",
                                "0:1:2:1",
                            ],
                        ],
                        "options": [],
                        "quantity": 1,
                    }
                ],
            }
        ],
    }

    imported = get_imported_configured_entries(
        data
    )

    package_definition = (
        ImportedProfilePackageDefinition(
            external_model_id=(
                "[army-of-lake-town] bard's-family"
            ),
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
    )

    mapped = map_imported_configured_entries(
        imported,
        structure_definitions={},
        package_definitions={
            (
                "[army-of-lake-town] "
                "bard's-family"
            ): package_definition,
        },
    )

    assert tuple(
        entry.profile_id
        for entry in mapped
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )

    assert all(
        entry.quantity == 1
        for entry in mapped
    )

    assert all(
        entry.warband_id == "BARD_WARBAND"
        for entry in mapped
    )

def test_bards_family_uses_production_package_map_by_default():
    entries = [
        ImportedConfiguredEntry(
            external_model_id=(
                "[army-of-lake-town] bard's-family"
            ),
            quantity=1,
            warband_id="BARD_WARBAND",
        )
    ]

    mapped = map_imported_configured_entries(
        entries,
        structure_definitions={},
    )

    assert tuple(
        entry.profile_id
        for entry in mapped
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )