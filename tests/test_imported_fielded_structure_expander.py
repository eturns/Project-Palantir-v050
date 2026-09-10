from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
)
from imported_fielded_structure_expander import (
    expand_imported_fielded_structure,
)


def test_expander_maps_root_and_member_profiles():
    entry = ImportedConfiguredEntry(
        external_model_id="EXT_MUMAK",
        external_option_ids=("EXT_OPTION",),
        quantity=1,
        warband_id="WARBAND_A",
    )

    definition = ImportedFieldedStructureDefinition(
        external_model_id="EXT_MUMAK",
        root_profile_id="WAR_MUMAK",
        member_profile_ids=(
            "HARADRIM_COMMANDER",
        ),
    )

    result = expand_imported_fielded_structure(
        entry=entry,
        definition=definition,
    )

    assert len(result) == 2

    root_entry = result[0]
    member_entry = result[1]

    assert root_entry.profile_id == "WAR_MUMAK"
    assert root_entry.external_option_ids == (
        "EXT_OPTION",
    )
    assert root_entry.quantity == 1
    assert root_entry.warband_id == "WARBAND_A"

    assert member_entry.profile_id == (
        "HARADRIM_COMMANDER"
    )
    assert member_entry.external_option_ids == ()
    assert member_entry.quantity == 1
    assert member_entry.warband_id == (
        "WARBAND_A"
    )


def test_expander_preserves_quantity_for_all_components():
    entry = ImportedConfiguredEntry(
        external_model_id="EXT_MUMAK",
        quantity=2,
        warband_id="WARBAND_A",
    )

    definition = ImportedFieldedStructureDefinition(
        external_model_id="EXT_MUMAK",
        root_profile_id="WAR_MUMAK",
        member_profile_ids=(
            "HARADRIM_COMMANDER",
        ),
    )

    result = expand_imported_fielded_structure(
        entry=entry,
        definition=definition,
    )

    assert tuple(
        expanded_entry.quantity
        for expanded_entry in result
    ) == (
        2,
        2,
    )


def test_expander_preserves_warband_for_all_components():
    entry = ImportedConfiguredEntry(
        external_model_id="EXT_MUMAK",
        quantity=1,
        warband_id="WARBAND_A",
    )

    definition = ImportedFieldedStructureDefinition(
        external_model_id="EXT_MUMAK",
        root_profile_id="WAR_MUMAK",
        member_profile_ids=(
            "HARADRIM_COMMANDER",
        ),
    )

    result = expand_imported_fielded_structure(
        entry=entry,
        definition=definition,
    )

    assert tuple(
        expanded_entry.warband_id
        for expanded_entry in result
    ) == (
        "WARBAND_A",
        "WARBAND_A",
    )