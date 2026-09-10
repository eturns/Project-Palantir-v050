from dataclasses import dataclass


@dataclass(frozen=True)
class ImportedFieldedStructureDefinition:
    external_model_id: str
    root_profile_id: str
    member_profile_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.external_model_id:
            raise ValueError(
                "External model id must not be empty."
            )

        if not self.root_profile_id:
            raise ValueError(
                "Root profile id must not be empty."
            )

        if not self.member_profile_ids:
            raise ValueError(
                "Imported fielded structure must contain "
                "at least one member profile id."
            )

        if any(
            not profile_id
            for profile_id in self.member_profile_ids
        ):
            raise ValueError(
                "Member profile ids must not be empty."
            )