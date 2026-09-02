from matchup_archetype_catalogue import (
    CANONICAL_MATCHUP_ARCHETYPES,
)
from matchup_archetype_evaluator import (
    calculate_matchup_archetype_score,
)
from matchup_result import MatchupResult


def build_matchup_archetype_summary(
    *,
    results: tuple[MatchupResult, ...],
) -> tuple[tuple[str, float], ...]:
    return tuple(
        (
            archetype.id,
            calculate_matchup_archetype_score(
                archetype=archetype,
                results=results,
            ),
        )
        for archetype in CANONICAL_MATCHUP_ARCHETYPES
    )