import pytest

from imported_profile_package_member import (
    ImportedProfilePackageMember,
)


def test_imported_profile_package_member_preserves_identity():
    member = ImportedProfilePackageMember(
        profile_id="BAIN",
    )

    assert member.profile_id == "BAIN"
    assert member.option_ids == ()


def test_imported_profile_package_member_rejects_empty_profile_id():
    with pytest.raises(
        ValueError,
        match=(
            "Imported profile package member "
            "Profile ID must not be empty."
        ),
    ):
        ImportedProfilePackageMember(
            profile_id="",
        )