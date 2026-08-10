from importers.mesbg_list_builder_json_importer import (
    group_mapped_configured_entries,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)


def test_group_mapped_configured_entries_combines_identical_entries():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
        ),
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=3,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert grouped == [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=5,
        )
    ]


def test_group_mapped_configured_entries_preserves_distinct_options():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0723",),
            quantity=3,
        ),
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert len(grouped) == 2

    assert grouped[0].external_option_ids == (
        "OPT0723",
    )
    assert grouped[0].quantity == 3

    assert grouped[1].external_option_ids == (
        "OPT0724",
    )
    assert grouped[1].quantity == 2


def test_group_mapped_configured_entries_preserves_distinct_profiles():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
        ),
        MappedConfiguredEntry(
            profile_id="IH_CAP",
            external_option_ids=("OPT0724",),
            quantity=1,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert len(grouped) == 2


def test_group_mapped_configured_entries_handles_unconfigured_entries():
    entries = [
        MappedConfiguredEntry(
            profile_id="DG_AK",
            quantity=1,
        ),
        MappedConfiguredEntry(
            profile_id="DG_AK",
            quantity=1,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert grouped == [
        MappedConfiguredEntry(
            profile_id="DG_AK",
            quantity=2,
        )
    ]


def test_group_mapped_configured_entries_handles_empty_list():
    assert group_mapped_configured_entries(
        []
    ) == []

def test_group_mapped_configured_entries_ignores_option_order():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=(
                "OPT_A",
                "OPT_B",
            ),
            quantity=2,
        ),
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=(
                "OPT_B",
                "OPT_A",
            ),
            quantity=3,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert grouped == [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=(
                "OPT_A",
                "OPT_B",
            ),
            quantity=5,
        )
    ]