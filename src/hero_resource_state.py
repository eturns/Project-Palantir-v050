from dataclasses import dataclass


@dataclass(frozen=True)
class HeroResourceState:
    remaining_might: int = 0
    remaining_will: int = 0
    remaining_fate: int = 0

    def __post_init__(self) -> None:
        if self.remaining_might < 0:
            raise ValueError(
                "Remaining Might cannot be negative."
            )

        if self.remaining_will < 0:
            raise ValueError(
                "Remaining Will cannot be negative."
            )

        if self.remaining_fate < 0:
            raise ValueError(
                "Remaining Fate cannot be negative."
            )