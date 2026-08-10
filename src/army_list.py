from dataclasses import dataclass, field

from faction import Faction
from army_rule import ArmyRule

@dataclass
class ArmyList:

    id: str
    name: str

    faction: Faction

    profiles: list = field(default_factory=list)

    army_rules: list[ArmyRule] = field(
        default_factory=list,
    )

    def __str__(self):

        return self.name