from dataclasses import dataclass


@dataclass(frozen=True)
class ManoeuvrabilityInputs:
    movement: float
    base_size_mm: float