from dataclasses import dataclass
from enum import Enum


class LethalAimSpend(Enum):
    TO_HIT = "TO_HIT"
    TO_WOUND = "TO_WOUND"
    IN_THE_WAY = "IN_THE_WAY"


@dataclass(frozen=True)
class LethalAimState:
    free_might_available: bool = True

    def can_spend_on(
        self,
        spend: LethalAimSpend,
    ) -> bool:
        return (
            self.free_might_available
            and isinstance(
                spend,
                LethalAimSpend,
            )
        )


def spend_lethal_aim_might(
    state: LethalAimState,
    spend: LethalAimSpend,
) -> LethalAimState:
    if not state.can_spend_on(
        spend,
    ):
        raise ValueError(
            "Lethal Aim free Might is not available "
            "for this spend."
        )

    return LethalAimState(
        free_might_available=False,
    )


def refresh_lethal_aim_for_new_turn() -> LethalAimState:
    return LethalAimState(
        free_might_available=True,
    )


def expire_lethal_aim_at_end_of_turn(
    state: LethalAimState,
) -> LethalAimState:
    return LethalAimState(
        free_might_available=False,
    )