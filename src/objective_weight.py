from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectiveWeight:
    name: str
    weight: float

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError(
                "Objective weight cannot be negative."
            )