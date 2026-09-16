import pytest

from imported_profile_package_definition import (
    ImportedProfilePackageDefinition,
)
from imported_profile_package_member import (
    ImportedProfilePackageMember,
)


def test_imported_profile_package_definition_preserves_package():
    definition = ImportedProfilePackageDefinition(
        external_model_id="EXT_BARDS_FAMILY",
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

    assert definition.external_model_id == "EXT_BARDS_FAMILY"
    assert definition.points == 60
    assert tuple(
        member.profile_id
        for member in definition.members
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )


def test_imported_profile_package_definition_requires_members():
    with pytest.raises(
        ValueError,
        match=(
            "Imported profile package must contain "
            "at least one member."
        ),
    ):
        ImportedProfilePackageDefinition(
            external_model_id="EXT_PACKAGE",
            points=60,
            members=(),
        )