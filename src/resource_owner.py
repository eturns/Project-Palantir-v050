from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceOwner:
    fielded_model_id: str

    def __post_init__(self) -> None:
        if not self.fielded_model_id:
            raise ValueError(
                "Resource owner fielded model id must not be empty."
            )

    @property
    def key(self) -> str:
        return self.fielded_model_id