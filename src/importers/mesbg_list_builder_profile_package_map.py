from imported_profile_package_definition import (
    ImportedProfilePackageDefinition,
)
from imported_profile_package_member import (
    ImportedProfilePackageMember,
)


IMPORTED_PROFILE_PACKAGE_DEFINITIONS = {
    "[army-of-lake-town] bard's-family": (
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
    ),
}