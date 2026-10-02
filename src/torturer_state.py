from dataclasses import dataclass


@dataclass(frozen=True)
class TorturerState:
    kills_in_combat: int = 0

    def __post_init__(self) -> None:
        if self.kills_in_combat < 0:
            raise ValueError(
                "Torturer kill count cannot be negative."
            )

    @property
    def rerolls_natural_ones_to_wound(self) -> bool:
        return self.kills_in_combat >= 1

    @property
    def gains_terror(self) -> bool:
        return self.kills_in_combat >= 3

    @property
    def rerolls_all_failed_to_wound(self) -> bool:
        return self.kills_in_combat >= 5