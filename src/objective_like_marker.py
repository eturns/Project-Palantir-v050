from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectiveLikeMarker:
    id: str
    is_normal_objective: bool
    objective_like_for: frozenset[str]

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError(
                "id must be a str."
            )

        if not self.id.strip():
            raise ValueError(
                "id cannot be blank."
            )

        if not isinstance(
            self.is_normal_objective,
            bool,
        ):
            raise TypeError(
                "is_normal_objective must be a bool."
            )

        if not isinstance(
            self.objective_like_for,
            frozenset,
        ):
            raise TypeError(
                "objective_like_for must be a frozenset."
            )

        if not all(
            isinstance(value, str)
            and value.strip()
            for value in self.objective_like_for
        ):
            raise TypeError(
                "objective_like_for must contain only non-blank strings."
            )

    def counts_as_objective_for(
        self,
        use: str,
    ) -> bool:
        if not isinstance(use, str):
            raise TypeError(
                "use must be a str."
            )

        if not use.strip():
            raise ValueError(
                "use cannot be blank."
            )

        if self.is_normal_objective:
            return True

        return use in self.objective_like_for