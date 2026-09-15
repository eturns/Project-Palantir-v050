from dataclasses import dataclass


@dataclass(frozen=True)
class ResurrectionConfig:
    resurrection_capable_models: int
    starting_models: int
    resilience_weight: int | float
    necromancer_remaining_will: int | None = None
    distance_inches: float | None = None
    will_points_available_to_spend: int = 0