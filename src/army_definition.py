from dataclasses import dataclass, field


@dataclass(frozen=True)
class ArmyEntryDefinition:
    """
    Identifies a configured Profile and its required quantity
    before resolving it into a runtime ArmyEntry.

    External option IDs preserve configuration imported from
    an external roster until ProfileOption entities are resolved.
    """

    profile_id: str
    quantity: int = 1
    external_option_ids: tuple[str, ...] = ()


@dataclass
class ArmyDefinition:
    """
    Represents a saved or imported army composition.
    """

    id: str
    name: str
    army_list_id: str
    points_limit: int | None
    leader_warband_id: str | None = None
    leader_profile_id: str | None = None

    entries: list[ArmyEntryDefinition] = field(
        default_factory=list,
    )