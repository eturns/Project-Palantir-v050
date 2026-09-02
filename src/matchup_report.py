from dataclasses import dataclass

from matchup_archetype_catalogue import (
    CANONICAL_MATCHUP_ARCHETYPES,
)
from matchup_recommendation import MatchupRecommendation
from matchup_result import MatchupResult


@dataclass(frozen=True)
class MatchupReport:
    strongest_archetype_id: str
    strongest_archetype_name: str
    strongest_score: float
    strongest_results: tuple[MatchupResult, ...]
    weakest_archetype_id: str
    weakest_archetype_name: str
    weakest_score: float
    weakest_results: tuple[MatchupResult, ...]


def build_matchup_report(
    *,
    recommendation: MatchupRecommendation,
    results: tuple[MatchupResult, ...],
) -> MatchupReport:
    archetypes_by_id = {
        archetype.id: archetype
        for archetype in CANONICAL_MATCHUP_ARCHETYPES
    }

    strongest_archetype = archetypes_by_id[
        recommendation.strongest_archetype_id
    ]

    weakest_archetype = archetypes_by_id[
        recommendation.weakest_archetype_id
    ]

    strongest_results = tuple(
        result
        for result in results
        if result.target_profile_id
        in strongest_archetype.profile_ids
    )

    weakest_results = tuple(
        result
        for result in results
        if result.target_profile_id
        in weakest_archetype.profile_ids
    )

    return MatchupReport(
        strongest_archetype_id=(
            recommendation.strongest_archetype_id
        ),
        strongest_archetype_name=(
            recommendation.strongest_archetype_name
        ),
        strongest_score=recommendation.strongest_score,
        strongest_results=strongest_results,
        weakest_archetype_id=(
            recommendation.weakest_archetype_id
        ),
        weakest_archetype_name=(
            recommendation.weakest_archetype_name
        ),
        weakest_score=recommendation.weakest_score,
        weakest_results=weakest_results,
    )