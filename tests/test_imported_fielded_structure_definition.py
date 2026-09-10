import pytest

from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
)


def test_imported_fielded_structure_definition_preserves_values():
    definition = ImportedFieldedStructureDefinition(
        external_model_id="EXT_MUMAK",
        root_profile_id="WAR_MUMAK",
        member_profile_ids=(
            "HARADRIM_COMMANDER",
        ),
    )

    assert definition.external_model_id == (
        "EXT_MUMAK"
    )
    assert definition.root_profile_id == (
        "WAR_MUMAK"
    )
    assert definition.member_profile_ids == (
        "HARADRIM_COMMANDER",
    )


def test_imported_fielded_structure_definition_rejects_empty_external_model_id():
    with pytest.raises(
        ValueError,
        match="External model id must not be empty",
    ):
        ImportedFieldedStructureDefinition(
            external_model_id="",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )


def test_imported_fielded_structure_definition_rejects_empty_root_profile_id():
    with pytest.raises(
        ValueError,
        match="Root profile id must not be empty",
    ):
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )


def test_imported_fielded_structure_definition_rejects_empty_members():
    with pytest.raises(
        ValueError,
        match=(
            "Imported fielded structure must contain "
            "at least one member profile id"
        ),
    ):
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(),
        )


def test_imported_fielded_structure_definition_rejects_empty_member_profile_id():
    with pytest.raises(
        ValueError,
        match="Member profile ids must not be empty",
    ):
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=("",),
        )