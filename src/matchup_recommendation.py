from dataclasses import dataclass

from matchup_archetype_catalogue import (
    CANONICAL_MATCHUP_ARCHETYPES,
)


@dataclass(frozen=True)
class MatchupRecommendation:
    strongest_archetype_id: str
    strongest_archetype_name: str
    strongest_score: float
    weakest_archetype_id: str
    weakest_archetype_name: str
    weakest_score: float


def build_matchup_recommendation(
    *,
    archetype_summary: tuple[
        tuple[str, float],
        ...
    ],
) -> MatchupRecommendation | None:
    if not archetype_summary:
        return None

    archetype_names = {
        archetype.id: archetype.name
        for archetype in CANONICAL_MATCHUP_ARCHETYPES
    }

    strongest_archetype_id, strongest_score = max(
        archetype_summary,
        key=lambda item: item[1],
    )

    weakest_archetype_id, weakest_score = min(
        archetype_summary,
        key=lambda item: item[1],
    )

    return MatchupRecommendation(
        strongest_archetype_id=strongest_archetype_id,
        strongest_archetype_name=archetype_names[
            strongest_archetype_id
        ],
        strongest_score=strongest_score,
        weakest_archetype_id=weakest_archetype_id,
        weakest_archetype_name=archetype_names[
            weakest_archetype_id
        ],
        weakest_score=weakest_score,
    )