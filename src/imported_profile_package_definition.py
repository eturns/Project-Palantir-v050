from dataclasses import dataclass

from imported_profile_package_member import (
    ImportedProfilePackageMember,
)


@dataclass(frozen=True)
class ImportedProfilePackageDefinition:
    external_model_id: str
    points: int
    members: tuple[
        ImportedProfilePackageMember,
        ...,
    ]

    def __post_init__(self) -> None:
        if not self.external_model_id:
            raise ValueError(
                "External model id must not be empty."
            )

        if self.points < 0:
            raise ValueError(
                "Imported profile package points "
                "must not be negative."
            )

        if not self.members:
            raise ValueError(
                "Imported profile package must contain "
                "at least one member."
            )