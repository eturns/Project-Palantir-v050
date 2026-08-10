from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from importers.mesbg_list_builder_json_importer import (
    map_imported_configured_entries,
)
from importers.mesbg_list_builder_profile_id_map import (
    EXTERNAL_PROFILE_IDS,
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