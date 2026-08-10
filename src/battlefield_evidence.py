from dataclasses import dataclass, field

@dataclass
class BattlefieldEvidence:
    """
    All battlefield evidence collected for an army.

    This object is populated by the Battlefield Evidence
    Collector and later consumed by the metric engine.
    """

    available_special_rules: list = field(
        default_factory=list,
    )   

    available_heroic_actions: list = field(
        default_factory=list,
    )

    available_spells: list = field(
        default_factory=list,
    )

    available_army_rules: list = field(
        default_factory=list,
    )

    def available_abilities(self) -> list:
        """
        Returns every available battlefield ability contained
        within this evidence object.
        """

        abilities = []

        abilities.extend(
            self.available_special_rules,
        )

        abilities.extend(
            self.available_heroic_actions,
        )

        abilities.extend(
            self.available_spells,
        )   
        abilities.extend(
            self.available_army_rules,
        )

        return abilities