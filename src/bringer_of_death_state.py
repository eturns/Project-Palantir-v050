from dataclasses import dataclass


@dataclass(frozen=True)
class BringerOfDeathState:
    kills_in_combat: int = 0

    def __post_init__(self) -> None:
        if self.kills_in_combat < 0:
            raise ValueError(
                "Bringer of Death kill count "
                "cannot be negative."
            )

    @property
    def gains_terror(self) -> bool:
        return self.kills_in_combat >= 2

    @property
    def gains_harbinger_of_evil(self) -> bool:
        return self.kills_in_combat >= 5

    @property
    def gains_mighty_hero(self) -> bool:
        return self.kills_in_combat >= 8