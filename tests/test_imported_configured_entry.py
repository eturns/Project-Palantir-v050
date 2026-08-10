from imported_configured_entry import (
    ImportedConfiguredEntry,
)


def test_imported_configured_entry_stores_configuration():
    entry = ImportedConfiguredEntry(
        external_model_id=(
            "[the-iron-hills] iron-hills-warrior"
        ),
        external_option_ids=("OPT0724",),
        quantity=2,
    )

    assert entry.external_model_id == (
        "[the-iron-hills] iron-hills-warrior"
    )
    assert entry.external_option_ids == ("OPT0724",)
    assert entry.quantity == 2


def test_imported_configured_entry_defaults_to_unconfigured_single_model():
    entry = ImportedConfiguredEntry(
        external_model_id=(
            "[the-iron-hills] iron-hills-chariot"
        ),
    )

    assert entry.external_option_ids == ()
    assert entry.quantity == 1


def test_imported_configured_entry_rejects_empty_model_id():
    try:
        ImportedConfiguredEntry(
            external_model_id="",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty external model ID."
        )


def test_imported_configured_entry_rejects_invalid_quantity():
    try:
        ImportedConfiguredEntry(
            external_model_id=(
                "[the-iron-hills] iron-hills-warrior"
            ),
            quantity=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for quantity below one."
        )