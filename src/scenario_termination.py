from dataclasses import dataclass
from scenario_definition import (
    ScenarioDefinition,
    TerminationType,
)

@dataclass(frozen=True)
class ScenarioTerminationResult:
    has_ended: bool
    reason: str | None

    def __post_init__(self) -> None:
        if not isinstance(
            self.has_ended,
            bool,
        ):
            raise TypeError(
                "has_ended must be a bool."
            )

        if self.has_ended and self.reason is None:
            raise ValueError(
                "Ended scenario termination result requires a reason."
            )

        if not self.has_ended and self.reason is not None:
            raise ValueError(
                "Non-ended scenario termination result cannot have a reason."
            )

def evaluate_quarter_strength_termination(
    first_army_at_quarter_strength: bool,
    second_army_at_quarter_strength: bool,
) -> ScenarioTerminationResult:
    if not isinstance(
        first_army_at_quarter_strength,
        bool,
    ):
        raise TypeError(
            "first_army_at_quarter_strength must be a bool."
        )

    if not isinstance(
        second_army_at_quarter_strength,
        bool,
    ):
        raise TypeError(
            "second_army_at_quarter_strength must be a bool."
        )

    if (
        first_army_at_quarter_strength
        or second_army_at_quarter_strength
    ):
        return ScenarioTerminationResult(
            has_ended=True,
            reason="quarter_strength",
        )

    return ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )

def evaluate_broken_random_termination(
    first_army_broken: bool,
    second_army_broken: bool,
    end_roll: int | None,
) -> ScenarioTerminationResult:
    if not isinstance(
        first_army_broken,
        bool,
    ):
        raise TypeError(
            "first_army_broken must be a bool."
        )

    if not isinstance(
        second_army_broken,
        bool,
    ):
        raise TypeError(
            "second_army_broken must be a bool."
        )

    eligible = (
        first_army_broken
        or second_army_broken
    )

    if not eligible:
        if end_roll is not None:
            raise ValueError(
                "end_roll must be None when neither army is Broken."
            )

        return ScenarioTerminationResult(
            has_ended=False,
            reason=None,
        )

    if end_roll is None:
        raise ValueError(
            "end_roll is required when at least one army is Broken."
        )

    if not isinstance(
        end_roll,
        int,
    ) or isinstance(
        end_roll,
        bool,
    ):
        raise TypeError(
            "end_roll must be an int or None."
        )

    if not 1 <= end_roll <= 6:
        raise ValueError(
            "end_roll must be between 1 and 6."
        )

    if end_roll <= 2:
        return ScenarioTerminationResult(
            has_ended=True,
            reason="broken_random",
        )

    return ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )

def evaluate_scenario_termination(
    termination_type: TerminationType,
    first_army_at_quarter_strength: bool,
    second_army_at_quarter_strength: bool,
    first_army_broken: bool,
    second_army_broken: bool,
    end_roll: int | None,
    scenario_id: str | None = None,
    artefacts_removed: int | None = None,
) -> ScenarioTerminationResult:
    if not isinstance(
        termination_type,
        TerminationType,
    ):
        raise TypeError(
            "termination_type must be a TerminationType."
        )

    if termination_type is TerminationType.QUARTER_STRENGTH:
        return evaluate_quarter_strength_termination(
            first_army_at_quarter_strength=(
                first_army_at_quarter_strength
            ),
            second_army_at_quarter_strength=(
                second_army_at_quarter_strength
            ),
        )

    if termination_type is TerminationType.BROKEN_RANDOM:
        return evaluate_broken_random_termination(
            first_army_broken=first_army_broken,
            second_army_broken=second_army_broken,
            end_roll=end_roll,
        )

    if termination_type is TerminationType.SCENARIO_SPECIFIC:
        if scenario_id is None:
            if artefacts_removed is None:
                raise NotImplementedError(
                    "Scenario-specific termination requires a dedicated handler."
                )

            raise ValueError(
                "scenario_id is required for scenario-specific termination."
            )

        if scenario_id == "SEIZE_THE_PRIZES":
            if artefacts_removed is None:
                raise ValueError(
                    "artefacts_removed is required for Seize the Prizes."
                )

            return evaluate_seize_the_prizes_termination(
                artefacts_removed=artefacts_removed,
                first_army_at_quarter_strength=(
                    first_army_at_quarter_strength
                ),
                second_army_at_quarter_strength=(
                    second_army_at_quarter_strength
                ),
            )

        raise NotImplementedError(
            "No scenario-specific termination handler for: "
            f"{scenario_id}"
        )

    raise ValueError(
        f"Unsupported termination type: {termination_type}"
    )

def evaluate_scenario_definition_termination(
    scenario: ScenarioDefinition,
    first_army_at_quarter_strength: bool,
    second_army_at_quarter_strength: bool,
    first_army_broken: bool,
    second_army_broken: bool,
    end_roll: int | None,
    artefacts_removed: int | None = None,
) -> ScenarioTerminationResult:
    if not isinstance(
        scenario,
        ScenarioDefinition,
    ):
        raise TypeError(
            "scenario must be a ScenarioDefinition."
        )

    return evaluate_scenario_termination(
        termination_type=scenario.termination_type,
        scenario_id=scenario.id,
        first_army_at_quarter_strength=(
            first_army_at_quarter_strength
        ),
        second_army_at_quarter_strength=(
            second_army_at_quarter_strength
        ),
        first_army_broken=first_army_broken,
        second_army_broken=second_army_broken,
        end_roll=end_roll,
        artefacts_removed=artefacts_removed,
    )

def evaluate_seize_the_prizes_termination(
    artefacts_removed: int,
    first_army_at_quarter_strength: bool,
    second_army_at_quarter_strength: bool,
) -> ScenarioTerminationResult:
    if not isinstance(
        artefacts_removed,
        int,
    ) or isinstance(
        artefacts_removed,
        bool,
    ):
        raise TypeError(
            "artefacts_removed must be an int."
        )

    if not 0 <= artefacts_removed <= 3:
        raise ValueError(
            "artefacts_removed must be between 0 and 3."
        )

    if not isinstance(
        first_army_at_quarter_strength,
        bool,
    ):
        raise TypeError(
            "first_army_at_quarter_strength must be a bool."
        )

    if not isinstance(
        second_army_at_quarter_strength,
        bool,
    ):
        raise TypeError(
            "second_army_at_quarter_strength must be a bool."
        )

    if artefacts_removed == 3:
        return ScenarioTerminationResult(
            has_ended=True,
            reason="all_artefacts_removed",
        )

    if (
        first_army_at_quarter_strength
        and second_army_at_quarter_strength
    ):
        return ScenarioTerminationResult(
            has_ended=True,
            reason="both_armies_at_quarter_strength",
        )

    return ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )