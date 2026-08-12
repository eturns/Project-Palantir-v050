from dataclasses import dataclass

from objective_weight import ObjectiveWeight


@dataclass(frozen=True)
class ObjectivePreset:
    name: str
    weights: tuple[ObjectiveWeight, ...]

    def __post_init__(self) -> None:
        names = tuple(
            weight.name
            for weight in self.weights
        )

        if len(names) != len(set(names)):
            raise ValueError(
                "Objective preset cannot contain duplicate component names."
            )

        total_weight = sum(
            weight.weight
            for weight in self.weights
        )

        if abs(total_weight - 1.0) > 1e-9:
            raise ValueError(
                "Objective preset weights must sum to 1.0."
            )