from matchup_archetype import MatchupArchetype
from matchup_result import MatchupResult


def calculate_matchup_archetype_score(
    *,
    archetype: MatchupArchetype,
    results: tuple[MatchupResult, ...],
) -> float:
    matching_scores = tuple(
        result.score
        for result in results
        if result.target_profile_id
        in archetype.profile_ids
    )

    if not matching_scores:
        return 0.0

    return (
        sum(matching_scores)
        / len(matching_scores)
    )