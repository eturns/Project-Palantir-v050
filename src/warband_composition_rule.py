from dataclasses import dataclass
from profile_classification import HeroicStatus

@dataclass(frozen=True)
class WarbandCompositionRule:
    member_keywords: tuple[str, ...] = ()
    member_races: tuple[str, ...] = ()
    member_factions: tuple[str, ...] = ()
    member_heroic_statuses: tuple[HeroicStatus, ...] = ()

    required_leader_keywords: tuple[str, ...] = ()
    required_leader_races: tuple[str, ...] = ()
    required_leader_factions: tuple[str, ...] = ()
    allowed_leader_profile_ids: tuple[str, ...] = ()
    required_leader_heroic_statuses: tuple[HeroicStatus, ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.member_keywords
            and not self.member_races
            and not self.member_factions
            and not self.member_heroic_statuses
        ):
            raise ValueError(
                "A warband composition rule needs at least "
                "one member selector."
            )

        if (
            not self.required_leader_keywords
            and not self.required_leader_races
            and not self.required_leader_factions
            and not self.required_leader_heroic_statuses
            and not self.allowed_leader_profile_ids
        ):
            raise ValueError(
                "A warband composition rule needs at least "
                "one permitted leader selector."
            )