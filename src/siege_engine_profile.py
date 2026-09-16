from dataclasses import dataclass


@dataclass(frozen=True)
class SiegeEngineProfile:
    id: str
    name: str
    points: int
    range_min: int
    range_max: int
    strength: int
    defence: int
    wounds: int
    base_size_mm: int
    size: str

    def __post_init__(self) -> None:
        if self.range_min < 0:
            raise ValueError(
                "Minimum range must not be negative."
            )

        if self.range_max <= self.range_min:
            raise ValueError(
                "Maximum range must be greater than minimum range."
            )

        if self.strength <= 0:
            raise ValueError(
                "Strength must be greater than zero."
            )

        if self.defence <= 0:
            raise ValueError(
                "Defence must be greater than zero."
            )

        if self.wounds <= 0:
            raise ValueError(
                "Wounds must be greater than zero."
            )

        if self.base_size_mm <= 0:
            raise ValueError(
                "Base size must be greater than zero."
            )

        if self.size not in {
            "SMALL",
            "LARGE",
        }:
            raise ValueError(
                "Siege Engine size must be SMALL or LARGE."
            )