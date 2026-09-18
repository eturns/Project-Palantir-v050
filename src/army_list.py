from dataclasses import dataclass, field

from faction import Faction
from army_rule import ArmyRule
from warband_composition_rule import (
    WarbandCompositionRule,
)
from profile_quantity_relation_rule import (
    ProfileQuantityRelationRule,
)

@dataclass
class ArmyList:

    id: str
    name: str

    faction: Faction

    profiles: list = field(default_factory=list)

    army_rules: list[ArmyRule] = field(
        default_factory=list,
    )

    warband_composition_rules: tuple[
        WarbandCompositionRule,
        ...
    ] = ()

    profile_quantity_relation_rules: tuple[
        ProfileQuantityRelationRule,
        ...
    ] = ()

    profile_factions_by_id: dict[
        str,
        tuple[str, ...],
    ] = field(
        default_factory=dict,
    )

    def __str__(self):

        return self.name