from dataclasses import dataclass


@dataclass(frozen=True)
class PriceOfFailureState:
    declared: bool = False
    within_azog_range: bool = False

    @property
    def can_use(self) -> bool:
        return (
            self.declared
            and self.within_azog_range
        )