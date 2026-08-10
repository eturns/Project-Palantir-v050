from dataclasses import dataclass


@dataclass
class Faction:
    """
    A MESBG faction.
    """

    id: str
    name: str

    def __str__(self) -> str:
        return self.name