from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from importers.mesbg_list_builder_json_importer import (
    map_imported_configured_entries,
)


def test_map_dain_ironfoot():
    mapped = map_imported_configured_entries(
        [
            ImportedConfiguredEntry(
                external_model_id=(
                    "[the-iron-hills] "
                    "dain-ironfoot-lord-of-the-iron-hills"
                ),
            )
        ]
    )

    assert mapped[0].profile_id == "IH_DAIN"


def test_map_iron_hills_warrior():
    mapped = map_imported_configured_entries(
        [
            ImportedConfiguredEntry(
                external_model_id=(
                    "[the-iron-hills] "
                    "iron-hills-warrior"
                ),
            )
        ]
    )

    assert mapped[0].profile_id == "IH_WR"


def test_map_iron_hills_captain():
    mapped = map_imported_configured_entries(
        [
            ImportedConfiguredEntry(
                external_model_id=(
                    "[the-iron-hills] "
                    "iron-hills-captain"
                ),
            )
        ]
    )

    assert mapped[0].profile_id == "IH_CAP"


def test_map_iron_hills_goat_rider():
    mapped = map_imported_configured_entries(
        [
            ImportedConfiguredEntry(
                external_model_id=(
                    "[the-iron-hills] "
                    "iron-hills-goat-rider"
                ),
            )
        ]
    )

    assert mapped[0].profile_id == "IH_GR"


def test_map_iron_hills_chariot():
    mapped = map_imported_configured_entries(
        [
            ImportedConfiguredEntry(
                external_model_id=(
                    "[the-iron-hills] "
                    "iron-hills-chariot"
                ),
            )
        ]
    )

    assert mapped[0].profile_id == "IH_CHARIOT"

