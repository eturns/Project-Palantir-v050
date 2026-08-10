from dataclasses import dataclass


@dataclass(frozen=True)
class WoundTarget:
    first_roll: int
    second_roll: int | None = None

    def __post_init__(self) -> None:
        if not 3 <= self.first_roll <= 6:
            raise ValueError(
                "first_roll must be between 3 and 6"
            )

        if self.second_roll is not None:
            if self.first_roll != 6:
                raise ValueError(
                    "second_roll requires first_roll to be 6"
                )

            if not 4 <= self.second_roll <= 6:
                raise ValueError(
                    "second_roll must be between 4 and 6"
                )