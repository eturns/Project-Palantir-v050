from dataclasses import dataclass


@dataclass(frozen=True)
class MatchupResult:
    target_profile_id: str
    target_profile_name: str
    score: float
    offensive_score: float | None = None
    defensive_score: float | None = None