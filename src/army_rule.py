from dataclasses import dataclass, field

from ability_tag_assignment import AbilityTagAssignment
from ability_prerequisite_entity import AbilityPrerequisiteEntity


@dataclass
class ArmyRule:
    """
    An army-wide rule that contributes to battlefield capability.
    """

    id: str
    name: str

    ability_tags: list[AbilityTagAssignment] = field(
        default_factory=list,
    )

    prerequisites: list[AbilityPrerequisiteEntity] = field(
        default_factory=list,
    )

    def __str__(self) -> str:
        return self.name