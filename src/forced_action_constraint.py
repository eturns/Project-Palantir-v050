from dataclasses import dataclass
from enum import Enum

class ForcedActionType(Enum):
    CHARGE = "charge"


@dataclass(frozen=True)
class ForcedActionConstraint:
    action_type: ForcedActionType
    require_if_possible: bool

    def __post_init__(self) -> None:
        if not isinstance(
            self.action_type,
            ForcedActionType,
        ):
            raise TypeError(
                "action_type must be a ForcedActionType."
            )

        if not isinstance(
            self.require_if_possible,
            bool,
        ):
            raise TypeError(
                "require_if_possible must be a bool."
            )

@dataclass(frozen=True)
class ForcedActionConstraint:
    action_type: ForcedActionType
    require_if_possible: bool

    def __post_init__(self) -> None:
        if not isinstance(
            self.action_type,
            ForcedActionType,
        ):
            raise TypeError(
                "action_type must be a ForcedActionType."
            )

        if not isinstance(
            self.require_if_possible,
            bool,
        ):
            raise TypeError(
                "require_if_possible must be a bool."
            )


@dataclass(frozen=True)
class ForcedActionTarget:
    id: str
    eligible: bool

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError(
                "id must be a str."
            )

        if not self.id.strip():
            raise ValueError(
                "id cannot be blank."
            )

        if not isinstance(self.eligible, bool):
            raise TypeError(
                "eligible must be a bool."
            )


def filter_forced_action_targets(
    *,
    constraint: ForcedActionConstraint,
    targets: tuple[ForcedActionTarget, ...],
    condition_met: bool = True,
) -> tuple[ForcedActionTarget, ...]:
    if not isinstance(
        constraint,
        ForcedActionConstraint,
    ):
        raise TypeError(
            "constraint must be a ForcedActionConstraint."
        )

    if not all(
        isinstance(target, ForcedActionTarget)
        for target in targets
    ):
        raise TypeError(
            "targets must contain only ForcedActionTarget values."
        )

    if not isinstance(condition_met, bool):
        raise TypeError(
            "condition_met must be a bool."
        )

    if not condition_met:
        return targets

    if not constraint.require_if_possible:
        return targets

    return tuple(
        target
        for target in targets
        if target.eligible
    )