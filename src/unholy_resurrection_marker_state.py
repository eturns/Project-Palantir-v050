from dataclasses import dataclass


@dataclass(frozen=True)
class UnholyResurrectionMarkerState:
    marker_count: int = 0

    def __post_init__(self) -> None:
        if self.marker_count < 0:
            raise ValueError(
                "Unholy Resurrection marker count cannot be negative."
            )

    @property
    def counted_models(self) -> int:
        return self.marker_count

    @property
    def objective_models(self) -> int:
        return 0