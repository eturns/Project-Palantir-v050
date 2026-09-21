from dataclasses import dataclass


@dataclass(frozen=True)
class VictoryPointModifier:
    amount: int
    maximum_total: int | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.amount, int)
            or isinstance(self.amount, bool)
        ):
            raise TypeError(
                "amount must be an int."
            )

        if self.maximum_total is not None:
            if (
                not isinstance(self.maximum_total, int)
                or isinstance(self.maximum_total, bool)
            ):
                raise TypeError(
                    "maximum_total must be an int or None."
                )

            if self.maximum_total < 0:
                raise ValueError(
                    "maximum_total cannot be negative."
                )


def apply_victory_point_modifier(
    *,
    current_points: int,
    modifier: VictoryPointModifier,
    condition_met: bool,
) -> int:
    if (
        not isinstance(current_points, int)
        or isinstance(current_points, bool)
    ):
        raise TypeError(
            "current_points must be an int."
        )

    if current_points < 0:
        raise ValueError(
            "current_points cannot be negative."
        )

    if not isinstance(
        modifier,
        VictoryPointModifier,
    ):
        raise TypeError(
            "modifier must be a VictoryPointModifier."
        )

    if not isinstance(condition_met, bool):
        raise TypeError(
            "condition_met must be a bool."
        )

    if not condition_met:
        return current_points

    result = current_points + modifier.amount

    if modifier.maximum_total is not None:
        result = min(
            result,
            modifier.maximum_total,
        )

    return result