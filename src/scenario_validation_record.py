from dataclasses import dataclass

from optimiser_candidate import OptimiserCandidate


@dataclass(frozen=True)
class ScenarioValidationRecord:
    candidate: OptimiserCandidate
    composition: tuple[tuple[str, int], ...]
    total_score: float
    pool_scores: tuple[tuple[str, float], ...]


def build_scenario_validation_record(
    *,
    candidate: OptimiserCandidate,
    objective,
) -> ScenarioValidationRecord:
    score = objective.score(
        candidate,
    )

    composition = tuple(
        (
            entry.profile.id,
            entry.quantity,
        )
        for entry in candidate.army.entries
    )

    pool_scores = tuple(
        (
            contribution.name,
            contribution.value,
        )
        for contribution in score.contributions
    )

    return ScenarioValidationRecord(
        candidate=candidate,
        composition=composition,
        total_score=score.total,
        pool_scores=pool_scores,
    )

def build_scenario_validation_records(
    *,
    candidates,
    objective,
) -> tuple[ScenarioValidationRecord, ...]:
    return tuple(
        build_scenario_validation_record(
            candidate=candidate,
            objective=objective,
        )
        for candidate in candidates
    )

def rank_scenario_validation_records(
    records: tuple[ScenarioValidationRecord, ...],
) -> tuple[ScenarioValidationRecord, ...]:
    return tuple(
        sorted(
            records,
            key=lambda record: record.total_score,
            reverse=True,
        )
    )

def scenario_validation_extremes(
    ranked_records: tuple[ScenarioValidationRecord, ...],
    *,
    count: int,
) -> tuple[
    tuple[ScenarioValidationRecord, ...],
    tuple[ScenarioValidationRecord, ...],
]:
    top = ranked_records[:count]

    bottom = ranked_records[
        len(ranked_records) - count:
    ]

    return top, bottom