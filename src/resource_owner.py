from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceOwner:
    profile_id: str
    instance_index: int

    def __post_init__(self) -> None:
        if self.instance_index < 1:
            raise ValueError(
                "Resource owner instance index must be at least 1."
            )

    @property
    def key(self) -> str:
        return (
            f"{self.profile_id}:"
            f"{self.instance_index}"
        )