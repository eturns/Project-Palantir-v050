from dataclasses import dataclass


@dataclass(frozen=True)
class ArmyPurchaseDefinition:
    id: str
    points: int
    quantity: int = 1
    warband_id: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError(
                "Army purchase definition ID "
                "must not be empty."
            )

        if self.points < 0:
            raise ValueError(
                "Army purchase definition points "
                "must not be negative."
            )

        if self.quantity < 1:
            raise ValueError(
                "Army purchase definition quantity "
                "must be at least one."
            )

    def total_points(self) -> int:
        return self.points * self.quantity