from dataclasses import dataclass


@dataclass(frozen=True)
class ImportedFieldedStructureMember:
    profile_id: str
    option_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError(
                "Imported fielded structure member "
                "Profile ID must not be empty."
            )

        if any(
            not option_id
            for option_id in self.option_ids
        ):
            raise ValueError(
                "Imported fielded structure member "
                "option IDs must not be empty."
            )