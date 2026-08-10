from mapped_configured_entry import (
    MappedConfiguredEntry,
)


def test_mapped_configured_entry_stores_configuration():
    entry = MappedConfiguredEntry(
        profile_id="IH_WR",
        external_option_ids=("OPT0724",),
        quantity=2,
    )

    assert entry.profile_id == "IH_WR"
    assert entry.external_option_ids == (
        "OPT0724",
    )
    assert entry.quantity == 2


def test_mapped_configured_entry_defaults_to_single_unconfigured_model():
    entry = MappedConfiguredEntry(
        profile_id="IH_CHARIOT",
    )

    assert entry.external_option_ids == ()
    assert entry.quantity == 1


def test_mapped_configured_entry_rejects_empty_profile_id():
    try:
        MappedConfiguredEntry(
            profile_id="",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Profile ID."
        )


def test_mapped_configured_entry_rejects_zero_quantity():
    try:
        MappedConfiguredEntry(
            profile_id="IH_WR",
            quantity=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for zero quantity."
        )


def test_mapped_configured_entry_is_immutable():
    entry = MappedConfiguredEntry(
        profile_id="IH_WR",
    )

    try:
        entry.quantity = 2
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected MappedConfiguredEntry "
            "to be immutable."
        )