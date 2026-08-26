from dataclasses import dataclass
from enum import Enum


class ScenarioPool(Enum):
    HOLD_OBJECTIVE = "hold_objective"
    KILL_THE_ENEMY = "kill_the_enemy"
    MAELSTROM_OF_BATTLE = "maelstrom_of_battle"
    OBJECT = "object"
    MANOEUVRING = "manoeuvring"
    UNIQUE = "unique"


class DeploymentType(Enum):
    STANDARD = "standard"
    MAELSTROM = "maelstrom"
    SPLIT = "split"
    REINFORCEMENTS = "reinforcements"


class TerminationType(Enum):
    QUARTER_STRENGTH = "quarter_strength"
    BROKEN_RANDOM = "broken_random"
    SCENARIO_SPECIFIC = "scenario_specific"


class ScenarioRule(Enum):
    MAELSTROM_OF_BATTLE = "maelstrom_of_battle"
    DARK_OF_NIGHT = "dark_of_night"
    A_TIME_OF_HEROES = "a_time_of_heroes"


@dataclass(frozen=True)
class ScenarioDefinition:
    id: str
    name: str
    pool: ScenarioPool
    deployment_type: DeploymentType
    termination_type: TerminationType
    special_rules: tuple[ScenarioRule, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Scenario ID cannot be blank."
            )

        if not self.name.strip():
            raise ValueError(
                "Scenario name cannot be blank."
            )

        if not isinstance(
            self.pool,
            ScenarioPool,
        ):
            raise TypeError(
                "pool must be a ScenarioPool."
            )

        if not isinstance(
            self.deployment_type,
            DeploymentType,
        ):
            raise TypeError(
                "deployment_type must be a DeploymentType."
            )

        if not isinstance(
            self.termination_type,
            TerminationType,
        ):
            raise TypeError(
                "termination_type must be a TerminationType."
            )

        if not all(
            isinstance(rule, ScenarioRule)
            for rule in self.special_rules
        ):
            raise TypeError(
                "special_rules must contain only ScenarioRule values."
            )
