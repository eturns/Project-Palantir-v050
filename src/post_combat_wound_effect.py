from dataclasses import dataclass


@dataclass(frozen=True)
class PostCombatWoundEffect:
    additional_wound_on_roll: int | None = None

    def __post_init__(self) -> None:
        if self.additional_wound_on_roll is not None:
            if not 1 <= self.additional_wound_on_roll <= 6:
                raise ValueError(
                    "Additional wound trigger must be between 1 and 6."
                )