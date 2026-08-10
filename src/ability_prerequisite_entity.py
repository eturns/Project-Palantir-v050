from dataclasses import dataclass


@dataclass(frozen=True)
class AbilityPrerequisiteEntity:
    """
    Represents an Ability Prerequisite.
    """

    id: str
    name: str