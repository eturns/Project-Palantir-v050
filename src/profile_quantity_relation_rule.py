from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileQuantityRelationRule:
    limited_profile_id: str
    reference_profile_id: str

    def __post_init__(self) -> None:
        if not self.limited_profile_id.strip():
            raise ValueError(
                "limited_profile_id cannot be empty."
            )

        if not self.reference_profile_id.strip():
            raise ValueError(
                "reference_profile_id cannot be empty."
            )