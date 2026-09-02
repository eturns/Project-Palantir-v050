from dataclasses import dataclass


@dataclass(frozen=True)
class MatchupArchetype:
    id: str
    name: str
    profile_ids: tuple[str, ...]