from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSpecialRuleAssignment:
    rule_id: str
    parameter: int | str | None = None

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError(
                "Runtime special rule ID cannot be empty."
            )