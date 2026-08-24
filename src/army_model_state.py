from dataclasses import dataclass


@dataclass(frozen=True)
class ArmyModelState:
    starting_models: int
    remaining_models: int

    def __post_init__(self) -> None:
        if self.starting_models < 0:
            raise ValueError(
                "Starting model count cannot be negative."
            )

        if self.remaining_models < 0:
            raise ValueError(
                "Remaining model count cannot be negative."
            )

        if self.remaining_models > self.starting_models:
            raise ValueError(
                "Remaining model count cannot exceed starting model count."
            )